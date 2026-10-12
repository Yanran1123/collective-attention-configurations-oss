
import mongoengine


alias_core = 'core'
db = 'db1_small'


# Just call this function in the main program to execute the connection
def global_init():
    # If we use multiple databases, we can set alias for them
    # Assign the name of the specific database to use to the parameter name
    mongoengine.register_connection(alias=alias_core, name=db)
    # mongoengine.register_connection(alias='analytics', db='demo_dealership_visits')


