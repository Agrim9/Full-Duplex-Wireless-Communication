#include "data_types.h"
#include "dma_setup.h"
#include "i2s_setup.h"
#include "register_system.h"
#include "register_cpu.h"
#include "aic3204.h"
#include "util_func.h"

#define PLL_100M 1 /* Set PLL system clock to 100MHz */
#define PLL_98M  0
#define PLL_40M  0
#define PLL_12M  0


Int16 PingPongFlagInL;  //these flag will be high when DMA has finished transferring data into PONG buffer  
Int16 PingPongFlagInR;  //these flags are being modified by DMA_ISR() function
Int16 PingPongFlagOutL;
Int16 PingPongFlagOutR;
Int16 overlap=FILTER_LENGTH;
/* Buffers for DMA in/out */
Int16 DMA_InpL[PING_PONG_SIZE];     //first half of these buffer will be used as PING buffer
Int16 DMA_InpR[PING_PONG_SIZE];     //second part will be used as PONG buffer
Int16 DMA_OutL[PING_PONG_SIZE];
Int16 DMA_OutR[PING_PONG_SIZE];

/* Buffers for processing */
Int16 rtl_sig[FFT_LENGTH];
Int16 tx_sig[FFT_LENGTH];
// Add declarations of your own buffers here for uniformity.

Int16 pad_coef[FFT_LENGTH];
Int16 temp_t[FFT_LENGTH];
Int16 past_vals[FILTER_LENGTH];
Int16 amp_X,amp_Y, insig_ptr;
Int16 matrix_X[FFT_LENGTH][FILTER_LENGTH+1];
Int16 matrix_XTX[FILTER_LENGTH+1][FILTER_LENGTH+1];
Int16 rtl_product[FILTER_LENGTH];
Int16 filter_coef[FILTER_LENGTH];
Int16 insig[FILTER_LENGTH+FFT_LENGTH];

Int16 BufferL_out[FFT_LENGTH];


void InitSystem(void);
void ConfigPort(void);
void SYS_GlobalIntEnable(void);
void SYS_GlobalIntDisable(void);
void do_fft(Int16 *real_data, Int16 *fft_real, Int16 *fft_imag, Uint16 scale);
void do_ifft(Int16 *fft_real, Int16 *fft_imag, Int16 *ifft_data, Uint16 scale);
void invert_matrix(Int16 X[FFT_LENGTH][FILTER_LENGTH+1]);
/* Choose AIC3204 sampling rate */
short fs = AIC3204_FS_48KHZ;

void main(void) 
{
    Uint16 i,j,k;
    float temp=0,temp2=0;

    InitSystem();
    ConfigPort();

    SYS_GlobalIntEnable(); /* Enable global interrupts */
    IER0 = 0x0100;         /* Enable DMA0 interrupt */

    I2S0_setup();          /* Setup I2S0 */

    AIC3204_Init();        /* Initialize AIC3204 */

    DMA0_setup();          /* Setup DMA0 CH0-3 */

    I2S0_enable();         /* Enable I2S0 */
    DMA0_enable_CH(0);     /* Enable DMA0CH0 */
 
    DMA0_enable_CH(1);     /* Enable DMA0CH1 */

    DMA0_enable_CH(2);     /* Enable DMA0CH2 */

    DMA0_enable_CH(3);     /* Enable DMA0CH3 */

    for(i=0;i<FILTER_LENGTH;i++)
    {
        past_vals[i]=0;
    }
    /* Begin infinite loop */
    while (1)
    {
        /********************* Capturing Inputs *************************/
        //Getting Inputs
        if (PingPongFlagInL && PingPongFlagInR)
        {
            for (i = 0; i < PING_PONG_SIZE/2; i++)
            {
                rtl_sig[i] = DMA_InpL[i + PING_PONG_SIZE/2];
                tx_sig[i] = DMA_InpR[i + PING_PONG_SIZE/2];
            }

        }
        else
        {
            for (i = 0; i < PING_PONG_SIZE/2; i++)
            {
                rtl_sig[i] = DMA_InpL[i];
                tx_sig[i] = DMA_InpR[i];
            }

        }
        /********************* Estimating Frequency Offset *************/

        //do_fft(rtl_sig, fft_rtl_R, fft_rtl_I, 1);
        //do_fft(tx_sig, fft_tx_R, fft_tx_I, 1);

        /********************Channel Estimation*************************/
        
        //Normalistion with max value observed so far
        amp_X=array_max(tx_sig,FFT_LENGTH);
        amp_Y=array_max(rtl_sig,FFT_LENGTH);
        for(i=0;i<FFT_LENGTH;i++)
        {
            rtl_sig[i]=rtl_sig[i]/amp_Y;
            tx_sig[i]=tx_sig[i]/amp_X;
        }

        //Filling Insig
        for(k=0;k<(FFT_LENGTH+FILTER_LENGTH);k++)
        {
            if(k<FILTER_LENGTH)
            {
                insig[k]=past_vals[k];
            }
            else
            {
                insig[FILTER_LENGTH+k]=tx_sig[k-FILTER_LENGTH];
            }
        }

        //Splicing to form matrix X
        insig_ptr=0;
        for(i=0;i<FILTER_LENGTH;i++)
        {
            for(j=0;j<=FFT_LENGTH;j++)
            {
                if(j!=FILTER_LENGTH)
                {
                    matrix_X[j][i]=insig[j+insig_ptr];

                }
                else
                {
                    matrix_X[j][i]=1;

                }
            }
            insig_ptr++;

        }

        //Obtain XtX and RTL Product
        for(i=0;i<=FILTER_LENGTH;i++)
        {
            for(j=0;j<=FILTER_LENGTH;j++)
            {
                temp=0,temp2=0;
                for(k=0;k<FFT_LENGTH;k++)
                {
                    temp+=matrix_X[k][i]*matrix_X[k][j];
                    if(i==0)
                    {
                    //To avoid wasteful calculations
                    temp2+=matrix_X[k][j]*rtl_sig[k];
                    }
                }
                if(i==0)
                {
                rtl_product[j]=temp2;
                }
                matrix_XTX[i][j]=temp;
            }
        }

        invert_matrix(matrix_XTX); //Passed via Reference

        for(i=0;i<=FILTER_LENGTH;i++)
        {
            temp=0;
            for(j=0;j<FILTER_LENGTH;j++)
            {
                temp+=matrix_XTX[i][j]*rtl_product[j];
            }
            filter_coef[i]=temp;
        }
        /********We have now obtained Filter Coefficients**********************/

          // Save the current input buffer for future reference.

        if (PingPongFlagOutL && PingPongFlagOutR)
        {

            for (i = 0; i < PING_PONG_SIZE/2; i++)
            {
                DMA_OutL[i + PING_PONG_SIZE/2] = BufferL_out[i+overlap];
                DMA_OutR[i + PING_PONG_SIZE/2] = BufferL_out[i+overlap];
            }
        } 
        else 
        {
            for (i = 0; i < PING_PONG_SIZE/2; i++)
            {                                
                DMA_OutL[i] = BufferL_out[i+overlap]; 
                DMA_OutR[i] = BufferL_out[i+overlap];
            }
        }

        for(i=0;i<FILTER_LENGTH;i++){
         past_vals[i]=tx_sig[i];
        }
    }

}

void invert_matrix(Int16 XtX[FILTER_LENGTH+1][FILTER_LENGTH+1])
{
    int i,j,index,k;
    float d, lambda = 0.01;
    int N=FILTER_LENGTH+1;
   
    Int16 a[FILTER_LENGTH+1][2*FILTER_LENGTH+2];
    for (i=0;i<N;i++)
    {
        for(j=0;j<2*N;j++)
        {
            if(j<N)
            {
                a[i][j]=XtX[i][j];
            }
            else
            {
                if((j-i)==N) a[i][j]=lambda;
                else a[i][j]=0;
            }
        }
    }

    for (i = 0; i < N; i++)

    {
        if(a[i][i]==0)
        {
            index = i;
            for (j = i; j < N; j++)
            {
            if (a[j][i]*a[j][i] > a[index][i]*a[index][i]) // See who is larger in magnitude
                index = j;
            }

            for (j = 0; j < N*2; j++)
            {
                d = a[i][j];
                a[i][j] = a[index][j];
                a[index][j] = d;
            }
        }



        for (j = 0; j < N; j++)   // limit was 2N before
            if (j != i)
            {
                d = a[j][i] / a[i][i];
                for (k = 0; k < N*2; k++)
                    a[j][k] -= a[i][k] * d;
            }

    }

    /************** reducing to unit matrix *************/

    for (i = 0; i < N; i++)
    {
        d = a[i][i];
        for (j = 0; j < N*2; j++)
            a[i][j] = a[i][j] / d;
    }

    //Storing Result in XtX
    for(i=0;i<N;i++)
    {
        for(j=N;j<2*N;j++)
        {
            XtX[i][j-N]=a[i][j];
        }
    }
    //As XtX is passed by ref, changes willbe conveyed back

}

/* ======================== Initialize DSP System Clock =========================  */
/* ------------------------------------------------------------------------------  */
/* For more info see SPRUFX5D - Section 1.4.3.2.6 (copying below for reference:)   */
/* You can follow the steps below to program the PLL of the DSP clock generator.   */ 
/* The recommendation is to stop all peripheral operation before changing the PLL  */ 
/* frequency, with the exception of the device CPU and USB. The device CPU must be */
/* operational to program the PLL controller. Software is responsible for ensuring */
/* the PLL remains in BYPASS_MODE for at least 4 ms before switching to PLL_MODE.  */
/* 1. Make sure the clock generator is in BYPASS MODE by setting SYSCLKSEL = 0.    */
/* 2. Program RDRATIO, M, and RDBYPASS in CGCR1 and CGCR2 according to your        */
/*    required settings.                                                           */
/* 3. Program ODRATIO and OUTDIVEN in CGCR4 according to your required settings.   */
/* 4. Write 0806h to the INIT field of CGCR3.                                      */
/* 5. Set PLL_PWRDN = 0.                                                           */
/* 6. Wait 4 ms for the PLL to complete its phase-locking sequence.                */
/* 7. Place the clock generator in its PLL MODE by setting SYSCLKSEL = 1.          */
/* ------------------------------------------------------------------------------  */
/* Note: This is a suggested sequence. It is most important to have all            */
/* programming done before the last step to place the clock generator in PLL MODE. */
/* =============================================================================== */
void InitSystem(void)
{
    Uint16 i;

    /*Clock Configuration Register 2 (CCR2) - Section 1.4.4.6 */
    CONFIG_MSW = 0x0; /* System Clock Generator is in Bypass Mode */

#if  (PLL_100M == 1)
    /* CGCR2 - Section 1.4.4.2 */
    PLL_CNTL2 = 0x8000; /* Bypass reference divider */
    /* CGCR4 - Section 1.4.4.4 */
    PLL_CNTL4 = 0x0000; /* Bypass output divider */
    /* CGCR3 - Section 1.4.4.3 */
    PLL_CNTL3 = 0x0806; /* initialization bits */
    /* CGCR1 - Section 1.4.4.1 */
    /* PLL power up. PLL Multiplier M = 1000 */
    PLL_CNTL1 = 0x8BE8; //PG1.4: 0x82FA;

#elif (PLL_12M == 1)
    PLL_CNTL2 = 0x8000;
    PLL_CNTL4 = 0x0200;
    PLL_CNTL3 = 0x0806;
    PLL_CNTL1 = 0x82ED;

#elif (PLL_98M == 1)    
    PLL_CNTL2 = 0x8000;
    PLL_CNTL4 = 0x0000;
    PLL_CNTL3 = 0x0806;
    PLL_CNTL1 = 0x82ED;

#elif (PLL_40M == 1)        
    PLL_CNTL2 = 0x8000;
    PLL_CNTL4 = 0x0300;
    PLL_CNTL3 = 0x0806;
    PLL_CNTL1 = 0x8262;    
#endif

    while ( (PLL_CNTL3 & 0x0008) == 0);
    
    /*Clock Configuration Register 2 (CCR2) - Section 1.4.4.6 */
    CONFIG_MSW = 0x1; /* System Clock Generator is in PLL Mode */

    /* Peripheral Clock Gating Configuration Register 1 (PCGCR1) - Section 1.5.3.2.1 */
    IDLE_PCGCR = 0x0020; /* System clock and other clocks active */
                         /* According to Table 1-24 bit 5 should be always set to 1 */
    /* Peripheral Clock Gating Configuration Register 2 (PCGCR2) - Section 1.5.3.2.1 */
    IDLE_PCGCR_MSW = 0x007D; /* Enable SAR clock */
    
    /* Peripheral Software Reset Counter Register (PSRCR) - Section 1.7.5.1 */
    PER_RSTCOUNT = 0x08; /* Software reset signals asserted after 2 clock cycles */
                         /* NOTE: p.75 states this value must be at least 0x08   */
    /* Peripheral Reset Control Register (PRCR) - Section 1.7.5.2 */
    PER_RESET = 0x00FF; /* Reset ALL peripherals */
    
    for (i=0; i< 0xFFFF; i++);
}

/* ========================= Configure External Busses ==========================  */
/* ------------------------------------------------------------------------------  */
/* For more info see SPRUFX5D - Section 1.7.3.1                                    */
/* =============================================================================== */
void ConfigPort(void)
{
    Int16 i;
    
    /* External Bus Selection Register (EBSR) - Section 1.7.3.1 */
    PERIPHSEL0 = 0x6900; /* PPMODE = 110 - Mode 6 */
                         /* SP1MODE = 10 - Mode 2 */
                         /* SP0MODE = 01 - Mode 1 */

    for (i=0; i< 0xFFF; i++);
}

void SYS_GlobalIntEnable(void)
{
    asm(" BIT (ST1, #ST1_INTM) = #0");
}

void SYS_GlobalIntDisable(void)
{
    asm(" BIT (ST1, #ST1_INTM) = #1");
}

