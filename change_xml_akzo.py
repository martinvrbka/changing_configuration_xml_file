from xml.dom import minidom

# Parse file
doc = minidom.parse(r'configuration.xml')
dispensers = doc.getElementsByTagName('DISPENSER')

# In case it's frontdesk, there is nothing to do
if len(dispensers) == 0:
    raise ValueError('Invalid dispenser file')


with open (r"configuration.xml", "w") as f:

    for colorant in doc.getElementsByTagName('COLORANT'):
        for canister in colorant.getElementsByTagName('CANISTER'):
            if canister.attributes['max_q'].value == "1500":
                canister.attributes['res_w'].value = "400.0000"
                canister.attributes['res_q'].value = "300.0000"
            for circuit in canister.getElementsByTagName('CIRCUIT'):
                for motors in circuit.getElementsByTagName('MOTORS'):
                    for motor in motors.getElementsByTagName('MOTOR'):
                        try:
                            motor.attributes['pause'].value = "5400"
                            motor.attributes['activity'].value = "60"
                        except Exception as e:
                            print(e)
    f.write(doc.toxml())
