from xml.dom import minidom

# Parse file
doc = minidom.parse(r'configuration.xml')
dispensers = doc.getElementsByTagName('DISPENSER')

# In case it's frontdesk, there is nothing to do
if len(dispensers) == 0:
    raise ValueError('Invalid dispenser file')

# Get colorants
policy = []
pause = []
activity = []

with open (r"configuration.xml", "w") as f:

    for colorant in doc.getElementsByTagName('COLORANT'):
        colorants_to_change = ["W-83", "W-73", "W-72", "W-84"]
        if colorant.attributes['code'].value in colorants_to_change:
            for canister in colorant.getElementsByTagName('CANISTER'):
                for circuit in canister.getElementsByTagName('CIRCUIT'):
                    for motors in circuit.getElementsByTagName('MOTORS'):
                        for motor in motors.getElementsByTagName('MOTOR'):
                            try:
                                motor.attributes['policy'].value = "0"
                                policy.append(motor.attributes['policy'].value)

                            except Exception as e:
                                print(e)
    f.write(doc.toxml())

print(policy)
print(len(policy))