from MilPython import *

class Battery(LPObject):
    '''Defines a simple battery storage system with a power-independent efficiency level'''
    def __init__(self, inputdata:LPInputdata,eta_charge=1,eta_discharge=1,name='',comment=''):
        super().__init__(inputdata,name,comment)
        self.p_discharge = self.add_time_var('P_bat_discharge','W',ub=3000)
        self.p_charge = self.add_time_var('P_bat_charge','W',ub=3000)
        self.E = self.add_time_var('E_el','Wh')
        self.bat_choice = self.add_decision_var_add(name='bat_choice',decision_dict={'bat1':{'price':1500,'e_max':200},'bat2':{'price':100,'e_max':50}})
        self.eta_charge=eta_charge
        self.eta_discharge=eta_discharge
    
    def def_equations(self):
        # Energy balance
        # Bat level in the time step - bat level in the last time step - Charging power * DeltaT * eta + Discharging power * DeltaT / eta = 0
        # First time step
        self.add_eq(var_lst=[[self.E,1,0],
                             [self.p_charge,- self.inputdata.dt_h * self.eta_charge,0],
                             [self.p_discharge,self.inputdata.dt_h * self.eta_discharge,0]],
                    sense='E',
                    b=0,
                    description='Bat. Energy Balance - first timestep')
        # All further time steps
        for t in range(1,self.inputdata.steps):
            self.add_eq(var_lst=[[self.E,1,t],
                                 [self.E,-1,t-1],
                                 [self.p_charge,- self.inputdata.dt_h * self.eta_charge,t],
                                 [self.p_discharge,self.inputdata.dt_h * self.eta_discharge,t]],
                        sense='E',
                        b=0,
                        description='Bat. energy balance')
        
        # max battery level
        for t in range(self.inputdata.steps):
            self.add_eq(var_lst=[[self.bat_choice.e_max,1],
                                 [self.E,-1,t]],
                        sense='>',
                        b=0,
                        description='Max. Bat. level')