#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
import RPAbase.RPAbase

class RPAUserService(RPAbase.RPAbase.RPAbase):
    """
    Sample pilot() loop for user -> serive order.
    """

    def prepare(self, name=__name__):
        super().prepare(name)
        random.seed()

    def pilot(self, user_group_name, service_group_name):
        driver, wait = self.pilot_setup()
        logger = self.logger
        appdict = self.appdict

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users_grp = self.config.get('users',{})
        users = users_grp.get(user_group_name,[])          # app group
        # Get service information
        svcs_grp = self.config.get('services',{})
        svcs = svcs_grp.get(service_group_name,[])             # app name
        if len(users) * len(svcs) == 0:
            self.logger.warn(f"No user({len(users)}) or service({len(svcs)}) is found.  exit.")
            return

        # main loop
        random.shuffle(users)
        for user in users:
            wk = ( str(user.get("name","")), str(user.get("id","")) )
            logger.info(f'処理開始: user=[name=>{wk[0]}<, id=>{wk[1]}<]')
            # ==============================
            if wk[0] not in svcs:
                logger.info(f"- User >{wk[0]}< does not use this service.  Skip.")
                continue
            #
            logger.debug(f'1.ログイン')
            # ==============================
            self.pilot_login(user)
            #
            logger.debug(f'2.処理本体')
            # ==============================
            self.pilot_internal(user)
            #
            logger.debug(f'3.ログアウト')
            # ==============================
            self.pilot_logout(user)
