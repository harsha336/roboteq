#!/usr/bin/env python
import roslib; roslib.load_manifest('roboteq_driver')
import rospy


from roboteq_msgs.msg import Feedback, Status
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue


MOTOR_OVERCURRENT = 160
MOTOR_OVERTEMP = 70
CH_OVERTEMP = 50
IC_OVERTEMP = 50

class RoboteqDiagnostics():
    def __init__(self):
        rospy.init_node('roboteq_diagnostics')
        self.diag_pub = rospy.Publisher('/diagnostics', DiagnosticArray)

        self.motor_desc = rospy.get_param('motor_desc','Unkown')

        rospy.Subscriber('/motors/front_left/status', Status, self.HandleSystemStatus)  
        rospy.Subscriber('/motors/front_left/feedback',Feedback, self.HandleSystemFeedback)

        self.last_diagnostics_time = rospy.get_rostime()

        self.roboteq_fault = []
        self.roboteq_status = []
        self.motor_current = []
        self.motor_rpm = []
        self.motor_power = []

        self.supply_volt = []
        self.supply_current = []
        self.sys_temp = []

    def publish_diag(self, time):

        if (time -self.last_diagnostics_time).to_sec() < 1.0:
            return
        self.last_diagnostics_time = time

        diag = DiagnosticArray()
        diag.header.stamp = time
        # Motor Status info
        if self.roboteq_fault:
            diag.status.append(self.roboteq_fault)
        if self.roboteq_status:
            diag.status.append(self.roboteq_status)
        if self.sys_temp:
            diag.status.append(self.sys_temp)

        # Motor Feedback Info
        if self.motor_current:
            diag.status.append(self.motor_current)
        if self.motor_rpm:
            diag.status.append(self.motor_rpm)
        if self.supply_volt:
            diag.status.append(self.supply_volt)
        if self.supply_current:
            diag.status.append(self.supply_current)
        if self.motor_power:
            diag.status.append(self.motor_power)


        print 'publishing diag'
        self.diag_pub.publish(diag)


    def HandleSystemStatus(self, data):
        self.roboteq_fault = DiagnosticStatus(name=self.motor_desc + " Motor Fault Status", level=DiagnosticStatus.OK, message="OK")
        fault = data.fault
        if fault == Status.FAULT_OVERHEAT:
            self.roboteq_fault.level = DiagnosticStatus.ERROR
            self.roboteq_fault.message = self.motor_desc + " Motor Controller overheat fault"
        elif fault==Status.FAULT_OVERVOLTAGE:
            self.roboteq_fault.level = DiagnosticStatus.ERROR
            self.roboteq_fault.message = self.motor_desc + " Motor controller overvoltage fault"
        elif fault==Status.FAULT_SHORT_CIRCUIT:
            self.roboteq_fault.level = DiagnosticStatus.ERROR
            self.roboteq_fault.message = self.motor_desc + " Motor controller short circuit fault"
        elif fault==Status.FAULT_MOSFET_FAILURE:
            self.roboteq_fault.level = DiagnosticStatus.ERROR
            self.roboteq_fault.message = self.motor_desc + " Motor controller mosfet failure fault"
        elif fault==Status.FAULT_UNDERVOLTAGE:
            self.roboteq_fault.level = DiagnosticStatus.WARN
            self.roboteq_fault.message = self.motor_desc + " Motor controller undervoltage fault"
        elif fault==Status.FAULT_EMERGENCY_STOP:
            self.roboteq_fault.level = DiagnosticStatus.WARN
            self.roboteq_fault.message = self.motor_desc + " Motor Controller emergency stop activated"
        elif fault==Status.FAULT_SEPEX_EXCITATION_FAULT:
            self.roboteq_fault.level = DiagnosticStatus.WARN
            self.roboteq_fault.message = self.motor_desc + " Motor Controller sepex excitation faulted"
        elif fault==Status.FAULT_STARTUP_CONFIG_FAULT:
            self.roboteq_fault.level = DiagnosticStatus.WARN
            self.roboteq_fault.message = self.motor_desc + " Motor Controller startup configuration is faulty"

        self.roboteq_status = DiagnosticStatus(name=self.motor_desc + " Motor Current Status", level=DiagnosticStatus.OK, message="OK")
        status = data.status
        if status == Status.STATUS_SERIAL_MODE:
            self.roboteq_status.message = self.motor_desc + " in Serial Mode"
        elif status == Status.STATUS_PULSE_MODE:
            self.roboteq_status.message = self.motor_desc + " in Pulse Mode"
        elif status == Status.STATUS_ANALOG_MODE:
            self.roboteq_status.message = self.motor_desc + " in Analog Mode"
        elif status == Status.STATUS_POWER_STAGE_OFF:
            self.roboteq_status.level = DiagnosticStatus.WARN
            self.roboteq_status.message = self.motor_desc + " motor_controller has its power stage off"
        elif status == Status.STATUS_STALL_DETECTED:
            self.roboteq_status.level = DiagnosticStatus.ERROR
            self.roboteq_status.message = self.motor_desc + " motor controller detected a stall"
        elif status == Status.STATUS_AT_LIMIT:
            self.roboteq_status.level = DiagnosticStatus.ERROR
            self.roboteq_status.message = self.motor_desc + " motor controller is at limit"
        elif status == Status.MICROBASIC_SCRIPT_RUNNING:
            self.roboteq_status.message = self.motor_desc + " motor controller is running a microbasic script"

        self.sys_temp = DiagnosticStatus(name=self.motor_desc + " motor system temperatures(Motor, Channel, Bridge IC)", level = DiagnosticStatus.OK, message = "OK")
        motor_temp = data.motor_temperature[0]
        ch_temp = data.channel_temperature[0]
        ic_temp = data.ic_temperature

        if (ch_temp > CH_OVERTEMP - 10):
            self.sys_temp.level = DiagnosticStatus.WARN
            self.sys_temp.message = self.motor_desc + " channel is approaching unsafe temperatures"
        if (ic_temp > IC_OVERTEMP - 10):
            self.sys_temp.level = DiagnosticStatus.WARN
            self.sys_temp.message = self.motor_desc + " bridge IC is approaching unsafe temperatures" 
        if (motor_temp > MOTOR_OVERTEMP - 20):
            self.sys_temp.level = DiagnosticStatus.WARN 
            self.sys_temp.message = self.motor_desc + " motor is approaching unsafe temperatures"
        if (ch_temp > CH_OVERTEMP):
            self.sys_temp.level = DiagnosticStatus.ERROR
            self.sys_temp.message = self.motor_desc + " channel above safe operating temperature"
        if (ic_temp > IC_OVERTEMP):
            self.sys_temp.level = DiagnosticStatus.ERROR
            self.sys_temp.message = self.motor_desc + " bridge IC is above safe operating temperature"
        #motor temperature is most important to report, so it overwrites previous warnings
        if (motor_temp > MOTOR_OVERTEMP):
            self.sys_temp.level = DiagnosticStatus.ERROR
            self.sys_temp.message = self.motor_desc + " motor above safe operating temperature"
       
        self.sys_temp.values = [KeyValue(self.motor_desc + " Motor temperature (C)", str(motor_temp)),
                                KeyValue(self.motor_desc + " Channel temperature (C)", str(ch_temp)),
                                KeyValue(self.motor_desc + " Bridge IC temperature (C)", str(ic_temp))]

        #Publish
        self.publish_diag(rospy.get_rostime())

                                
    def HandleSystemFeedback(self, data):
        #Motor Current
        self.motor_current = DiagnosticStatus(name=self.motor_desc + " Motor Current", level = DiagnosticStatus.OK, message="OK")

        current = data.motor_current[0]
        if (current > (MOTOR_OVERCURRENT - 20)):
            self.motor_current.level = DiagnosticStatus.WARN 
            self.motor_current.message = self.motor_desc + " Motor Current Very High"
        elif (current > MOTOR_OVERCURRENT):
            self.motor_current.level = DiagnosticStatus.ERROR
            self.motor_current.message = self.motor_desc + " Motor Current Dangerously High. Reduce torque requirement"

        self.motor_current.values = [KeyValue(self.motor_desc + "Current (A)", str(current))]

        #Motor RPM
        self.motor_rpm = DiagnosticStatus(name=self.motor_desc + " Motor RPM", level = DiagnosticStatus.OK, message="OK")
        rpm = data.encoder_rpm[0]
        self.motor_rpm.values = [KeyValue(self.motor_desc + " RPM",str(rpm))]
        
        #Supply Volt
        self.supply_volt = DiagnosticStatus(name=self.motor_desc + " Supply Volts", level=DiagnosticStatus.OK, message="OK")
        volt = data.supply_voltage
        self.supply_volt.values = [KeyValue(self.motor_desc + " Supply Volts (V)", str(volt))]

        #Supply Current
        self.supply_volt = DiagnosticStatus(name=self.motor_desc + " Supply Current", level=DiagnosticStatus.OK, message="OK")
        sup_current = data.supply_current
        self.supply_volt.values = [KeyValue(self.motor_desc + " Supply Current (A)", str(sup_current))]

        #Power Input
        self.motor_power = DiagnosticStatus(name=self.motor_desc + " Motor Power", level=DiagnosticStatus.OK, message="OK")
        mot_power = data.motor_power[0]
        self.motor_power.values = [KeyValue(self.motor_desc + "Motor Power (W)", str(mot_power))]

        self.publish_diag(rospy.get_rostime())

            
if __name__ == "__main__":
    obj = RoboteqDiagnostics()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
