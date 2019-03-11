#!/bin/bash
USB="/media/backupDrive/GIMLISERVER_01"

# assuming the stuff is in /var/www/html/*
# and needs to go to /media/toshiba/REDBOXBACKUP

echo "Backup at $(date +%a_%d.%m.%Y_%H:%M) to $USB"
# GIMLI DOES NOT USE SQL (right now and hopefully never)
#mysqldump -u starforce -p'forcestar' starforce > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/starforce_$(date +%a_%d.%m.%Y_%H.%M).sql
#mysqldump -u forcetech -p'techforce' forcetech > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/forcetech_$(date +%a_%d.%m.%Y_%H.%M).sql
#mysqldump -u pandaDB -p'blackwhitebear' pandaDB > /media/toshiba/REDBOXBACKUP/SQL_BACKUP/pandaDB_$(date +%a_%d.%m.%Y_%H.%M).sql
#echo "SQL databases dumped. Syncing files..."

echo "Syncing files..."
echo "$USB/SYNC"
rsync --progress -r -u -a /var/www/html/* "$USB/SYNC"
echo "All files synced."
echo "Removing mirror files.."
rm -r "$USB/MIRROR"
mkdir "$USB/MIRROR"
echo "Removing serverscript files.."
rm -r "$USB/ServerScripts"
mkdir "$USB/ServerScripts"
echo "Copy mirror files.."
cp -r /var/www/html/* "$USB/MIRROR"
echo "Copy serverscript files.."
cp -r /home/pi/ServerScripts/** "$USB/ServerScripts"

# Again, GIMLI does not use SQL
#echo "Removing overhead SQL..."
#cd /media/toshiba/REDBOXBACKUP/SQL_BACKUP/
#ls -1tr | head -n -30 | xargs -d '\n' rm -f --
#echo "..done."

# generate timestamp.
echo "Generate timestamp..."
echo $USB/*.backupTime
sudo rm $USB/*.backupTime
sudo touch $USB/LastUpdate_$(date +%a_%d.%m.%Y_%H.%M).backupTime
# again in the mirror directory.
#sudo rm /media/toshiba/REDBOXBACKUP/MIRROR/*.backupTime
#sudo touch /media/toshiba/REDBOXBACKUP/MIRROR/LastUpdate_$(date +%a_%d.%m.%Y_%H.%M).backupTime
echo "Timestamps generated."
echo $(date +%a_%d.%m.%Y_%H:%M)
echo "+++ BACKUP DONE +++"
