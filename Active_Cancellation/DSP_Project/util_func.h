Int16 array_max(Int16 *array, Int16 size)
{
	Int16 ctr=0,max=0;
	for(ctr=0;ctr<size;ctr++)
	{
		if(array[ctr]>max)
		{
			max=array[ctr];
		}
	}
	return max;
}

