#!/bin/sh
PRE=`date +%F-%H-%M-%S`
#Backup
echo "Create Package ..."
ssh $BLOG_HOST "LANG=C; cd $BLOG_WEB_PATH; tar czf $BLOG_WEB_PATH/backup.tar.gz blog"
echo "Downloading ..."
scp $BLOG_HOST:$BLOG_WEB_PATH/backup.tar.gz $BACKUP_PATH/$PRE.tar.gz
echo "Remove Package ..."
ssh $BLOG_HOST "LANG=C; cd $BLOG_WEB_PATH; rm $BLOG_WEB_PATH/backup.tar.gz"
echo "Done!"


