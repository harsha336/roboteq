#ifndef ROBOTEQ_SERIAL_CONTROLLER
#define ROBOTEQ_SERIAL_CONTROLLER

#include "ros/ros.h"
#include "std_msgs/String.h"
#include "roboteq/lightweightserial.h"
#include <unistd.h>
#include <iostream>
#include <sstream>
#include <pthread.h>

//#include "igvc_control/control_msg.h" //for messages
//#include "igvc_control/motor_diag.h"	

//#include "igvc_control/lightweightserial.h"
//#include <gsl/gsl_matrix.h>
//#include <gsl/gsl_linalg.h>
//#include <gsl/gsl_blas.h>
//#include "geometry_msgs/Vector3.h"
//#include "joy/Joy.h"

#define TRUE 1
#define FALSE 0

#define MCNTRL_PORT_1 "/dev/ttyACM0"
#define MCNTRL_PORT_2 "/dev/ttyACM1"


#define ASCII_CR_CODE 13
#define ASCII_ACK_CODE 43
/*
#define M1_MULT 1
#define M2_MULT -1

//Vehicle Parameters
#define c 0.385 //m half of the wheel base
#define l 0.4318 //m half of length
#define enc_wheel_rev 0.185 // (14/60) rpm conversion factor between encoder RPM's and wheel RPM's
#define r 0.13 //m wheel radius
#define x0 0.1 //x-coordinate of ICR (assuming constant slippage)
#define pi 3.14159

#define REQD_VX 0.5 //target forward velocity m/s
#define DEFAULT_K_YAW 4
#define DEFAULT_K_CNTRL 0.1
*/

using namespace std;

//bool autonomous=false;
//bool omniwheel=false;
//bool auto_velControl = false;
//double k_cntrl=DEFAULT_K_YAW; //controller gain
//double k_yaw = DEFAULT_K_CNTRL;; //yaw error controller gain
//void joystickCallback(const joy::Joy::ConstPtr& msg);
//void pathErrorCallback(const geometry_msgs::Vector3 msg);


//GSL Matrix Abstractions
//gsl_matrix* matrix_inverse(gsl_matrix *A);
//gsl_matrix* matrix_multiply(gsl_matrix *A, gsl_matrix *B);
//static void matrix_print(gsl_matrix *A);

//Nonlinear Path Tracker Variables
//void path_tracker();
//double yaw_e = 0; //current yaw error
//double cross_e=0; //currrent cross_track error
//double reqd_vel=0;



class roboteq {
	private :
	const char *serialPort;
	int controller_baud_;
	bool com_status_;
	std::string version;
		
	
	bool sendRuntimeCommand(string strCommand);
	bool sendSerial(string strQuery);
	LightweightSerial *controllerPort;

	bool runCallback(string *data);
	bool addCallback(bool (*func)(void));
	std::string last_command_sent_;//command is a type of message.

	public :
	
	int motor_speed_[2];
	double motor_current_[2];
	double batery_current_;
	double motor_commanded_[2];
	double drive_voltage_;
	double battery_voltage_;
	double analog_voltage_;
	long encoder_count_[2];
	int encoder_rpm_[2];
	int motor_power_[2];
	int status_flag_;
	int faut_flag_;
	float motor_temperature_[2];
	float channel_temperature_[2];
	float ic_temperature_;
	float closed_loop_err_;

	std::string user_var;
	roboteq();
	roboteq(const char *port, int baud);
	~roboteq();
	bool setupComm();
	bool setMotorSpeeds();
	bool getUserVariable();
	bool getVoltages();

	//To impliment
	//Runtime Commands
	bool resetDIOx(int i);
	bool setDIOx(int i);
	bool setSetpoint(int motor,int val);
	bool setSetpoint(int val);
	bool setEstop();
	bool resetEstop();
	bool setVAR(int i, int val);

	//Runtime Querys	
	bool getMotorCurrent();
	bool getAnalogValues();
	bool getAnalogValue(int i);
	bool getBatteryAmps();
	bool getEncoderCount();
//	bool getEncoderCountREL();
	bool getDigitalInputs();
	bool getDigitalOutputs();
	bool getClosedLoopError();
	//bool getFeedbackIn();
	bool getFault();
	bool getStatus();
	bool getMotorPower();
	bool getPulsedInputs();
	bool getMotorRPM();
	bool getTemp();
	bool getVolts();
	int readVAR();
	int readVAR(int i);
	bool controllerPresent();
	bool getMotorCommanded();
	void readserialbuss();
	bool getBatCurrent();
	


	

};


#endif
