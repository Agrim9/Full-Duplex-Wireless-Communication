INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SELF_CANCEL self_cancel)

FIND_PATH(
    SELF_CANCEL_INCLUDE_DIRS
    NAMES self_cancel/api.h
    HINTS $ENV{SELF_CANCEL_DIR}/include
        ${PC_SELF_CANCEL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SELF_CANCEL_LIBRARIES
    NAMES gnuradio-self_cancel
    HINTS $ENV{SELF_CANCEL_DIR}/lib
        ${PC_SELF_CANCEL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SELF_CANCEL DEFAULT_MSG SELF_CANCEL_LIBRARIES SELF_CANCEL_INCLUDE_DIRS)
MARK_AS_ADVANCED(SELF_CANCEL_LIBRARIES SELF_CANCEL_INCLUDE_DIRS)

