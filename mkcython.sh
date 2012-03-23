#!/bin/bash
# ~/bin/mkcython.sh
# @author: U{Jiahua Huang <jhuangjiahua@gmail.com>
# @license: LGPL
# 把 .py 编译为 .so
# 依赖 cython  python-dev
# 用法: mkcython.sh [-e] *.py
#    -e 编译为可执行
# 最后修改: 2007-07-10

[ "$1" = '-x' ] && { E=1 ; shift; }
[ "$1" = '-e' ] && { E=1 ; shift; }

[ -f "$1" ] || { echo Usage: $0 [-x] pyfile... ; exit ; }

which clang && CC=clang || CC=gcc

docython(){
    PYX="$1"
    MO=$(echo $PYX | sed 's/.pyx$//' | sed 's/.py$//')
    C="$MO.c"
    SO="$MO.so"
    set +x
    echo "+ cython --embed $PYX"
    cython --embed $PYX || exit 1
    sed -i 's/\/\*.o*\*\/$//g' "$C"
    if [ -n "$E" ]
    then
	set -x
	#gcc -pthread          -fno-strict-aliasing -O2  -Wstrict-prototypes -fPIC -I/usr/include/python2.6 -L/usr/lib/ -lpython2.6 "$C" -s -o "$MO"
	$CC         `python-config --cflags` `python-config --ldflags` "$C" -s -o "$MO"
    else
	set -x
    	#gcc -pthread -shared  -fno-strict-aliasing -O2  -Wstrict-prototypes -fPIC -I/usr/include/python2.6 -L/usr/lib/ -lpython2.6 "$C"  -s -o "$SO"
	$CC -shared `python-config --cflags` `python-config --ldflags` "$C" -s -o "$SO"
    fi
}

for i in "$@"
do
    [ -f "$i" ] && ( docython "$i" )
done

