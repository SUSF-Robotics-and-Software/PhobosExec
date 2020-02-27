import LocomotionControl.loco_ctrl as LocoCtrl

def cmd_none(state, cmd):
    return True

def cmd_safe(state, cmd):
    print('Rover safe')

    # TODO

    return True

def cmd_unsafe(state, cmd):
    print('Rover unsafe')

    # TODO

    return True

def cmd_mnvr(state, cmd):
    '''
    Handle a manouvre command
    '''

    # Build the manouvre command object
    mnvr_cmd = LocoCtrl.mnvr_cmd.MnvrCmd()

    if 'mnvr_id' not in cmd.keys():
        print('Error building manouvre command: the command must include a ' \
              'manouvre ID')
        return False

    try:
        mnvr_cmd.mnvr_id = LocoCtrl.mnvr_cmd.MnvrType[cmd['mnvr_id']]
        mnvr_cmd.mnvr_params = {}
    except:
        print(f'Error building manouvre command: {cmd["mnvr_id"]} is not a ' \
               'valid manouvre ID')
        return False
    
    # Build the proper list of parmaeters for each command type
    if mnvr_cmd.mnvr_id == LocoCtrl.constants.MnvrType.ACKERMAN or \
         mnvr_cmd.mnvr_id == LocoCtrl.constants.MnvrType.SKID_STEER:
        if 'rov_speed_mss_Lm' not in cmd.keys():
            print('Error building manouvre command: Ackerman or skid steer ' \
                  'commands must include a rov_speed_mss_Lm parameter')
            return False
        if 'curv_m_Rb' not in cmd.keys():
            print('Error building manouvre command: Ackerman or skid steer ' \
                  'commands must include a curv_m_Rb parameter')
            return False
        
        mnvr_cmd.mnvr_params['rov_speed_mss_Lm'] = cmd['rov_speed_mss_Lm']
        mnvr_cmd.mnvr_params['curv_m_Rb'] = cmd['curv_m_Rb']
    
    elif mnvr_cmd.mnvr_id == LocoCtrl.constants.MnvrType.POINT_TURN:
        if 'rov_rate_rads_Rb' not in cmd.keys():
            print('Error building manouvre command: point turn commands must' \
                  ' include a rov_rate_rads_Rb parameter')
            return False
        
        mnvr_cmd.mnvr_params['rov_rate_rads_Rb'] = cmd['rov_rate_rads_Rb']

    status_rpt = state.loco_ctrl.do_mnvr_ctrl(mnvr_cmd)
    
    if not status_rpt:
        return True
    else:
        # TODO: Process status report here
        return False