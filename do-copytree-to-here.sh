#!/bin/sh
# 按目录拷贝文件到这儿
#
# 如: cd skel ; do-copytree-to-here.sh `locate ooo-calc.png` .

# 这个是会拷贝目录内容
set -x
cp -av --parents "$@"

exit 0

# 下边是可以支持 对目录不拷贝内容，只创建目录结构
[ "$1" = '-h' ] && { echo "Usage: $0 SOURCE" ; exit 1 ; }--parents

copydir=0 # 拷贝目录内容/只创建目录

for i in "$@"; do
    if [ -d "$i" ] ; then
	mkdir -p -v "$i"
        [ "copydir" -eq 0 ] || cp -av $i "./$i" # 拷贝目录内容
    else
        mkdir -p -v `dirname "./$i"`
        cp -av "$i" "./$i"
    fi
done
