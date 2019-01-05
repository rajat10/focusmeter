BASE_URL = 'https://mpulsemobile.atlassian.net'


sample_confluence_doc = """
ACTUAL TOTAL Time to deploy: __ minutes.

Scheduled Release Date: 01/02/2018 LA, US ;  01/03/2018 New Delhi
Scheduled Release Time: 9pm PST

Scheduled Members Involved:
Pier 64
MPulse

Scheduled Maintenance window:

2nd January, 2019 (PST)

Release: 2nd January





Summary of Tickets:

Stories
MSXDEV-8174
MSXDEV-9503
MSXDEV-9468
MSXDEV-9231
MSXDEV-9150
MSXDEV-9531
MSXDEV-9547
MSXDEV-9500
MSXDEV-9480
MSXDEV-9462
MSXDEV-9460
MSXDEV-9452
MSXDEV-9316
MSXDEV-9474
MSXDEV-9505
MSXDEV-9466
MSXDEV-9439
MSXDEV-9540
MSXDEV-9507
MSXDEV-9470
MSXDEV-9502
MSXDEV-9508
MSXDEV-9510
MSXDEV-9183
MSXDEV-9529
MSXDEV-9377
MSXDEV-9516

Servers Involved on prod Environment:

ms5prod-proxy-001
ms5prod-cpanel-001
ms5prod-queue-001
ms5prod-comm-001
ms5prod-celery-001
ms5prod-db-001
ms5prod-log-001

prod Deployment Steps
1. Company announcement
2. Backup database (Pier 64)
3. Install (Pier 64)
 Assumption: Deploy runs on ms5prod-log-001, and from ms5prod-log-001 user can ssh login to all the other machines.

ssh login to ms5prod-log-001
copy the following checksum and save to file '/tmp/checksum'

sudo su - msx
cd /tmp
wget https://ms5-jenkins.mpulse.io/job/Package/4684/artifact/mobilestorm/msx-1.0.4684-20181228.tgz


install

sudo su - msx
cd /tmp
wget https://ms5-jenkins.mpulse.io/job/Package/4684/artifact/mobilestorm/install-1.0.4684.sh
chmod +x ./install-1.0.4684.sh
ENV=prod ./install-1.0.4684.sh



If the master secret service hasn't been started, or the password file for master secret service has been removed, the script will ask you to input the master secret twice for initializing.

If Command Center is deployed for first time, you will be asked to input email and password to create default admin user account.



Which should display:

[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: celerybeat                       RUNNING    pid11064, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: celeryd                          RUNNING    pid11063, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: gateway                          RUNNING    pid11065, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: jetty                            RUNNING    pid11060, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: tornado                          RUNNING    pid11062, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: healthcare-gateway               RUNNING    pid27333, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: sms-gateway                      RUNNING    pid27332, uptime0:03:06
[msx-app-002.msxtra.com|msx-app-002.msxtra.com] out: celeryd-sms-gateway              RUNNING    pid20658, uptime0:03:06




 The output is not the real output, only for demonstrating the format of the output.


"""