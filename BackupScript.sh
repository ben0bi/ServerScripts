#!/bin/bash
#set USB="/media/toshiba/REDBOXBACKUP/"

# assuming the stuff is in /var/www/html/*
# and needs to go to /media/toshiba/REDBOXBACKUP

echo "Backup at $(date +%a_%d.%m.%Y_%H:%M)"
mysqldump -u starforce -p'forcestar' starforce > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/starforce_$(date +%a_%d.%m.%Y_%H.%M).sql
mysqldump -u forcetech -p'techforce' forcetech > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/forcetech_$(date +%a_%d.%m.%Y_%H.%M).sql
mysqldump -u pandaDB -p'blackwhitebear' pandaDB > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/pandaDB_$(date +%a_%d.%m.%Y_%H.%M).sql

echo "SQL databases dumped. Syncing files..."
rsync --progress -r -u -a /var/www/html/* /media/toshiba/REDBOXBACKUP/MIRROR
echo "All files synced."

echo "Removing overhead SQL..."
cd /media/toshiba/REDBOXBACKUP/SQL_BACKUP/
ls -1tr | head -n -30 | xargs -d '\n' rm -f --
#sudo rm -f $(ls -1t /media/toshiba/REDBOXBACKUP/SQL_BACKUP/ | tail -n +31)
echo "..done."

# generate timestamp.
sudo rm /media/toshiba/REDBOXBACKUP/*.backupTime
sudo touch /media/toshiba/REDBOXBACKUP/LastUpdate_$(date +%a_%d.%m.%Y_%H.%M).backupTime
# again in the mirror directory.
sudo rm /media/toshiba/REDBOXBACKUP/MIRROR/*.backupTime
sudo touch /media/toshiba/REDBOXBACKUP/MIRROR/LastUpdate_$(date +%a_%d.%m.%Y_%H.%M).backupTime
echo "Timestamps generated."
echo $(date +%a_%d.%m.%Y_%H:%M)
echo "+++ BACKUP DONE +++"
