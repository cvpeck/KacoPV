/var/log/solar/* {
	weekly
	rotate 4 
	compress
	delaycompress
	missingok
	notifempty
	create 644 solar solar 
}
/var/log/alternatives.log {
        weekly
        rotate 4
        compress
        delaycompress
        missingok
        notifempty
        create 644 solar solar
}
