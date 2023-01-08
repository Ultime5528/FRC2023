# FRC2023 #
### Writing Conventions ###
* All code must be written in the English language
* Follow PyCharm style recommendations
* Commit names must be clear and informative
* Progress must be tracked with GitHub Projects (https://github.com/orgs/Ultime5528/projects/2)

* File names use lowercase without spaces
* Class names use PascalCase
* Function and variable names use snake_case
* Function and command names start with an action verb (get, set, move, start, stop...)
* Ports  
    * Must be added to ports.py
    * Respect the naming convention : "subsystem" _ "component type"  _ "precision"
    * Example : drivetrain_motor_left
* Properties 
  * Must be added to properties.py 
  * Respect the naming convention : "subsystem/command" \_ "variable type" _ "precision"
  * Example : intake_speed_slow, climber_height_max
  * ntproperty strings are the same as their variables, ex:
    * **shooter_speed** = ntproperty("/Properties/**shooter_speed**", 1500, ...

