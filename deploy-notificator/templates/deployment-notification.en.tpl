{% if first_name %}
Hi there {{ first_name }}!
{% else %}
Hi there!
{% endif %}
<br/><br/>
This is an automatic notification that new version:<br/>
	v{{ app_version }} of {{ app_name }}<br/>
has been deployed on the server.<br/>
<br/>
Have a nice day!<br/>
-- <br/>
This message has been sent automaticaly by {{ app_name }}<br/>
deployment notification system.<br/>
Copyright (C) TEONITE - http://teonite.com<br/>
