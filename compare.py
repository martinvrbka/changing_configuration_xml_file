from xml.dom import minidom

# Parse file
doc = minidom.parse(r'configuration.xml')
dispensers = doc.getElementsByTagName('DISPENSER')

motors = []

#for motor in doc.getElementsByTagName('MOTOR'):
#    try:
#        motors.append(motor.attributes("policy").value)
#    except:
#        pass

for motor in doc.getElementsByTagName('MOTOR'):
    try:
        motor.append(motor.attributes["policy"].value)
    except:
        pass


print(motors)