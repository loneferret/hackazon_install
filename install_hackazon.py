#!/usr/bin/python

# Description: Installs Rapid7's Hackazon web application semi-automatically
# Support OSs: Debain based
# Created: September 14th 2016
# Version: 0.1
# Author: Steven McElrea / @loneferret
#
# Comments: Will support other operating systems, I just need to install them.
# Also Hackazon is (at least for me) to get running on Ubuntu 16.04 Will get that
# in here as well.
#
# I also stole Dave's colour class.

import os
import subprocess
import sys

class constants:
	osVersion = "unknown"
	osVersionNumber = "unknown"
	dbPassword = "toor"
	installFolder = "/var/www/html/"

# Got the idea from PTF from Dave Kennedy
# https://github.com/trustedsec/ptf
# I just wrote colour correctly...
class bcolours:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERL = '\033[4m'
    ENDC = '\033[0m'
    backBlack = '\033[40m'
    backRed = '\033[41m'
    backGreen = '\033[42m'
    backYellow = '\033[43m'
    backBlue = '\033[44m'
    backMagenta = '\033[45m'
    backCyan = '\033[46m'



# Not very useful now but hopefully I'll add
# a few more operating systems later
def getOsVersion():
	# check to see if debian
	if os.path.isfile("/usr/bin/apt-get"):
		proc = subprocess.Popen(['lsb_release', '-d'], stdout=subprocess.PIPE)
		out = proc.communicate()
		osVer = out[0]
		constants.osVersion = "Debian\Ubuntu"
		if "Ubuntu" in (osVer.split("\t"))[1]:
			constants.osVersionNumber =  ((osVer.split("\t"))[1].split(" "))[1]

	return constants.osVersion + "\n" + (osVer.split("\t"))[1]

# For now just updates Debian based operating systems.
def updateOS():
	if "Debian" in constants.osVersion:
		print( bcolours.RED + "Executing apt-get update:" + bcolours.ENDC)
		subprocess.Popen('apt-get update', shell=True).wait()
		print( bcolours.GREEN + "Ok, finished updating.\n" + bcolours.ENDC)
		print( bcolours.RED + "Executing apt-get upgrade:" + bcolours.ENDC)
		subprocess.Popen('apt-get upgrade -y && apt-get autoclean -y && updatedb', shell=True).wait()
		print( bcolours.GREEN + "Ok, all upgraded time to install Hackazon stuff..." + bcolours.ENDC )
	else:
		print( "Not there yet sorry..." )
		sys.exit()

# Installs your basic LAMP server with a few additional
# packages such as git, php5-fpm
# For php7 would need to install: php-bcmath & php-mbstring
def lampInstall():
	# If Debian/Ubuntu check version to select proper packages
	if "Debian" in constants.osVersion:
		#[ lamp1415Install if constants.osVersionNumber==14 or constants.osVersionNumber==15 else lamp16Install() for x in [14,15,16]]
		if constants.osVersionNumber in ["14","15"]:
			lamp1415Install()
		else:
			lamp16Install()

def lamp1415Install():
	print( bcolours.RED + "Installing LAMP:" + bcolours.ENDC)
	mysqlPSW = raw_input(bcolours.BOLD + "Type MySQL password [toor]: " + bcolours.ENDC) or "toor"
	constants.dbPassword = mysqlPSW
	subprocess.Popen('echo "mysql-server mysql-server/root_password password ' +  mysqlPSW  + '" | sudo debconf-set-selections', shell=True).wait()
	subprocess.Popen('echo "mysql-server mysql-server/root_password_again password ' + mysqlPSW + '" | sudo debconf-set-selections', shell=True).wait()
	subprocess.Popen('apt-get install git apache2 php5-mysql mysql-server php5 libapache2-mod-php5 php5-mcrypt php5-fpm -y && apt-get autoclean -y && updatedb', shell=True).wait()
	print( bcolours.GREEN + "That should be it for packages..." + bcolours.ENDC )

def lamp16Install():
	print( bcolours.RED + "Installing LAMP:" + bcolours.ENDC)
	mysqlPSW = raw_input(bcolours.BOLD + "Type MySQL password [toor]: " + bcolours.ENDC) or "toor"
	constants.dbPassword = mysqlPSW
	# Set mysql password
	subprocess.Popen('echo "mysql-server mysql-server/root_password password ' +  mysqlPSW  + '" | sudo debconf-set-selections', shell=True).wait()
	subprocess.Popen('echo "mysql-server mysql-server/root_password_again password ' + mysqlPSW + '" | sudo debconf-set-selections', shell=True).wait()
	subprocess.Popen('apt-get install git apache2 php-mysql mysql-server php libapache2-mod-php php-cli php-mcrypt php-bcmath php-mbstring -y && apt-get autoclean -y && updatedb', shell=True).wait()
	print( bcolours.GREEN + "That should be it for packages..." + bcolours.ENDC )
	# This modifies the mysql.conf.d/mysqld.conf file
	print( bcolours.RED + "Fixing the NO_ZERO_DATE issue in mysqld.cnf file ..." + bcolours.ENDC )
	subprocess.Popen('echo \"sql_mode=ONLY_FULL_GROUP_BY,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION \" >> /etc/mysql/mysql.conf.d/mysqld.cnf', shell=True).wait()
	print( bcolours.GREEN + "Done; Restarting MySQL..." + bcolours.ENDC )
	subprocess.Popen('systemctl restart mysql', shell=True).wait()


# Get Hackazon from GitHub, and slap it in /var/www/html
# for now
def hackazonInstall():
	print( bcolours.RED + "Cloning Hackzon from Github.com" + bcolours.ENDC )
	location = raw_input( bcolours.BOLD + "Where to you want to install Hackazon? [/var/www/html/] " + bcolours.ENDC ) or "/var/www/html/"

	#if location != constants.installFolder:
	if os.path.isdir(location):
		constants.installFolder = location
	else:
		createFolder = raw_input( bcolours.BOLD + "The folder \"" + location + "\" does not exist. Want to create it? [Y/n] " + bcolours.ENDC )
		if createFolder == 'n':
			print( "Exiting..." )
			sys.exit()
		else:
			subprocess.Popen('mkdir -p ' + location, shell=True).wait()
			constants.installFolder = location
	#else:
	#	subprocess.Popen('mkdir -p ' + location, shell=True).wait()
	#	constants.installFolder = location

	if os.listdir(constants.installFolder):
		print( bcolours.RED + "This will delete the contents of " +  constants.installFolder + bcolours.ENDC )
		ans = raw_input( bcolours.BOLD + "Do you wish to continue? [Y/n] " + bcolours.ENDC )
		if ans == 'n':
			print( "Exiting..." )
			sys.exit()
		else:
			subprocess.Popen('rm -rf ' + constants.installFolder, shell=True).wait()

	subprocess.Popen('git clone https://github.com/rapid7/hackazon.git ' + constants.installFolder, shell=True).wait()
	command = "cp " + constants.installFolder + "assets/config/db.sample.php " + constants.installFolder + "assets/config/db.php"
	subprocess.Popen(command, shell=True).wait()
	print ( bcolours.GREEN + "Installing composer ..." + bcolours.ENDC )
	subprocess.Popen('php composer.phar self-update && php composer.phar install -o --prefer-dist', shell=True).wait()

	print ( bcolours.GREEN + "Editing db.php ..." + bcolours.ENDC )
	dbConf = constants.installFolder + "assets/config/db.php"
	dbFile = open(dbConf, 'r')
	data = dbFile.read()
	newContent = data.replace("\'user\'\=\>\'hackazon\'", "\'user\'\=\>\'root\'")
	newContent = newContent.replace("yourdbpass", constants.dbPassword)
	f = open(dbConf, 'w')
	f.write(newContent)
	f.close()




# Will modify 000-default.conf accordingly
def setupApache():
	print( bcolours.BOLD + "Setting up Apache..." + bcolours.ENDC )
	if "Debian" in constants.osVersion:
		subprocess.Popen('service apache2 stop && a2enmod rewrite && service apache2 start', shell=True).wait()

	siteConfig = os.getcwd() + "/" + "hackazon.text"
	confData = open(siteConfig, 'rw')
	data = confData.read()
	newContent = data.replace("CHANGEDOCUMENTROOT", constants.installFolder + "web/")
	newContent = newContent.replace("CHANGEDIRECTORY", constants.installFolder + "web")

	newFile = "/etc/apache2/sites-available/000-default.conf"
	if os.path.isfile(newFile):
		print ( bcolours.RED + "Deleting 000-default.conf" + bcolours.ENDC )
		subprocess.Popen('rm ' + newFile, shell=True).wait()

	print ( bcolours.GREEN + "Making new  000-default.conf file" + bcolours.ENDC )
	f = open(newFile, 'w')
	f.write(newContent)
	f.close()
	subprocess.Popen('chown -R www-data:www-data ' + constants.installFolder + " && service apache2 restart", shell=True).wait()


def banner():
	banner  = bcolours.BOLD + "This assumes a clean install, but will do its best to adjust" + bcolours.ENDC + "\n"
	banner += "[!] Please don\'t blame me if anything screws up, run this at your own risk" + "\n"

	return banner

def main():
	print ( banner() )
	print ( "Operating System:\n" + getOsVersion() )
	print ( "Running update..." )
	updateOS()
	installPackages = raw_input("Ready to install the LAMP server? [Y/n] ") or "Y"
	if installPackages == 'n':
		print( "Exiting..." )
		sys.exit()
	else:
		lampInstall()
		hackazonInstall()
		setupApache()


if __name__ == "__main__":
	main()
