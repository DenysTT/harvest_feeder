# Harvest_feeder

Install
-------

::

    # clone the repository
    $ git clone https://github.com/DenysTT/harvest_feeder.git
    
    # update template.json with your own data
    
    # build docker image
    $ make build release=test


Run
---

::

    # to generate access token and account id
    # log in to harvest web app with your credentials by the link https://id.getharvest.com/developers
    $ make run HARVEST_ACCESS_TOKEN=foo HARVEST_ACCOUNT_ID=bar release=test

Taste good with a CRON job =D
