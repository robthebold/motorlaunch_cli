#!/usr/bin/python3
""" 
    Text mode interactive interface to bimmerconnected library

    Copyright (C) 2019  Robert Bruce

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    Disclaimer: not endorsed or affiliated with BMW or the authors of bimmer_connected
    
    Support and encourage development:
    
    buy me coffee or electricity: paypal.me/zeppelinware
    and/or
    contribute: bug reports
    and/or
    contribute: translations/localizations
    and/or
    contribute: code

"""



import argparse
import logging
import json
import os
import time
import configparser
import getpass
from pathlib import Path
from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name, valid_regions, Regions
from bimmer_connected.vehicle import VehicleViewDirection

def main() -> None:
    """Main function."""
    
    print()
    print('Motorlaunch, Copyright (C) 2019 Robert Bruce.')
    print('A text mode interface to the bimmer_connected library,')
    print('this program provides access to services and information')
    print('from BMW ConnectedDrive.')
    print('This program is not endorsed or affiliated with BMW')
    print('or the developers of the bimmer_connected library.')
    print('Use of BMW services is the user\'s responsibility.')
    print()
    print('This program comes with ABSOLUTELY NO WARRANTY')
    print('This is free software,')
    print('and you are welcome to redistribute it')
    print('under certain conditions')
    print('For more info on license and warranty,')
    print('see https://www.gnu.org/licenses/gpl-3.0-standalone.html')
    print()
    print('This is alpha-quality software, and doesn\'t even have a')
    print('version number yet. Many inputs are not checked for proper')
    print('values. Incorrect entries will probably cause the program')
    print('to terminate. Errors returned by the BMW server whether yours')
    print('or theirs will usually also crash this program.')
    print('If your config file gets munged up and stuff won\'t work,')
    print('delete .motorlaunch/motorlaunch.ini from your home')
    print('directory and start over.')
    print()
    print('Not all features are available in all regions. All features')
    print('are subject to availabilty of BMW servers via the internet.')
    print('This program has not been tested anywhere outside the USA,')
    print('although the underlying library has been used worldwide.')
    print('Your mileage may vary.')
    print()
    print('All units are SI, this means l for volume and km for distance.')
    print()
    print('Your password is _not_ saved in the configuration.')
    print('To wipe your username and VIN from this computer,')
    print('simply delete \".motorlaunch/motorlaunch.ini\"')
    print('from your home directory with a method commensurate with')
    print('your security needs.')
    print()

    
    password = ''
    lat = 0.0
    long = 0.0
    home = str(Path.home())
    configdir = home+'/.motorlaunch'
    configfilename = configdir+'/motorlaunch.ini'
    
    config = configparser.ConfigParser()
    config['credentials'] = {'username': ''}
    config['region'] = {'region': 'nowhere'}
    config['language'] = {'language':'en_us'}
    config['vehicles'] = {'currentvin': ''}
    
    #Create config file directory if it doesn't already exist
    if not os.path.exists(configdir):
        os.mkdir(configdir)
    
    config.read(configfilename);
    #print('config sections {}'.format(config.sections()))
    username = config.get("credentials", "username")
    regionname = config.get('region','region')
    vin = config.get('vehicles','currentvin')
    
    print('Current username {}'.format(username))
    print('Selected region {}'.format(regionname))
    print('Selected VIN {}'.format(vin))
    print()
    
    if username and regionname:
        password = getpass.getpass(prompt="Please enter your password: ")
        account = ConnectedDriveAccount(username, password, get_region_from_name(regionname))
        account.update_vehicle_states()
        print()
        print('Found {} vehicles: {}'.format(len(account.vehicles),','.join([v.name for v in account.vehicles])))
        if vin:
            vehicle = account.get_vehicle(vin)
        else:
            for vehicle in account.vehicles:
                print('VIN: {}'.format(vehicle.vin))
                
        quick_status(vehicle)    
  
    else:
        print('Notice: Configuration file is empty.')
        print('Please set up your username and reqion')
        print('using functions 0 and 1, then')
        print('quit and restart motorlaunch.')
  
    printmenu()

    choice=input("Type an option ")
    print()
    while choice != 'q':
        print(choice)
        if choice == '0':
            print('Current Region is {}'.format(regionname))
            print('Select Region From {}'.format((valid_regions())))
            regionname=input("Type region ")
            for region_name, region in Regions.__members__.items():
                if regionname.lower() == region_name.lower():
                    print('Region {}'.format(region))
                    config['region']['region'] = region_name.lower()
        if choice == '1':
            print('Current username: {}'.format(username))
            username = input("Type your new username ")
            config['credentials']['username'] = username
        if choice == '2':
            print('Not implemented yet.')
        if choice == '3':
            if vehicle:
                print('Current vehicle {}'.format(vehicle.vin))
                vins=[]
                index = 1
                for vehicle in account.vehicles:
                    print('{} VIN: {} {}'.format(index,vehicle.vin,vehicle.name))
                    vins.append(vehicle.vin)
                    index += 1
                index=int(input('Enter number of vehicle to select. '))
                vehicle = account.get_vehicle(vins[index-1])
                config['vehicles']['currentvin'] = vehicle.vin
                print('Current vehicle is now {} {}'.format(vehicle.vin,vehicle.name))
                quick_status(vehicle)
            else:
                print('No vehicle selected.')
        if choice == '4':
            if vehicle:
                print('vehicle status: ')
                print('VIN: {}'.format(vehicle.vin))
                print('Doors:')
                print('  {}'.format(vehicle.state.attributes["doorLockState"]))
                print('    Driver Front: {}'.format(vehicle.state.attributes["doorDriverFront"]))
                print('    Driver Rear: {}'.format(vehicle.state.attributes["doorDriverRear"]))
                print('    Passenger Front: {}'.format(vehicle.state.attributes["doorPassengerFront"]))
                print('    Passenger Rear: {}'.format(vehicle.state.attributes["doorPassengerRear"]))
                print('Hood: {}'.format(vehicle.state.attributes["hood"]))
                print('Trunk: {}'.format(vehicle.state.attributes["trunk"]))
                print('Windows:')
                print('    Driver Front: {}'.format(vehicle.state.attributes["windowDriverFront"]))
                print('    Driver Rear: {}'.format(vehicle.state.attributes["windowDriverRear"]))
                print('    Passenger Front: {}'.format(vehicle.state.attributes["windowPassengerFront"]))
                print('    Passenger Rear: {}'.format(vehicle.state.attributes["windowPassengerRear"]))
                print('    Sunroof: {}'.format(vehicle.state.attributes["sunroof"]))
                print('    Rear: {}'.format(vehicle.state.attributes["rearWindow"]))
                print('Fuel:')
                print('    Remaining Fuel: {}/{}'.format(vehicle.state.attributes["remainingFuel"],vehicle.state.attributes["maxFuel"]))
                print('    Fuel Range: {}'.format(vehicle.state.attributes["remainingRangeFuel"]))
                print('Battery:')
                print('    Percent Remaining: {}'.format(vehicle.state.attributes["chargingLevelHv"]))
                print('    Electric Range: {}/{}'.format(vehicle.state.attributes["remainingRangeElectric"],vehicle.state.attributes["maxRangeElectric"]))
                print('')
                
            else:
                print('No vehicle selected.')
        if choice == '5':
            light_flash(vehicle)
        if choice == '6':
            sound_horn(vehicle)
        if choice == '7':
            if vehicle and vehicle.state.is_vehicle_tracking_enabled:
                print('Latitude {}, Longitude {}'.format(vehicle.state.gps_position[0],vehicle.state.gps_position[1]))
            else:
                print('I\'m sorry Dave, I\'m afraid I can\'t do that.')
        if choice == '8':
            vehicle.remote_services.trigger_remote_door_lock()
        if choice == '9':
            vehicle.remote_services.trigger_remote_door_unlock()
        if choice == 'a':
            vehicle.remote_services.trigger_remote_air_conditioning()
        if choice == 'o':
            password = input("Please enter your password: ")
            account = ConnectedDriveAccount(username, password, get_region_from_name(regionname))
            account.update_vehicle_states()
            print('Found {} vehicles: {}'.format(len(account.vehicles),','.join([v.name for v in account.vehicles])))
            for vehicle in account.vehicles:
                print('VIN: {}'.format(vehicle.vin))
                print('mileage: {}'.format(vehicle.state.mileage))
                print('Doors: {}'.format(vehicle.state.attributes["doorLockState"]))
                print('Position: {}'.format(vehicle.state.attributes["position"]["status"]))
            if vin:
                vehicle = account.get_vehicle(vin)
        if choice =='r':
            if vehicle:
                print('Raw status info (You asked for it):')
                print('VIN: {}'.format(vehicle.vin))
                print(json.dumps(vehicle.state.attributes, indent=4))
            else:
                print('No vehicle selected.')

        if choice =='i':
            if vehicle:
                print('Inquire a single status field:')
                field=input('Carefully type exact field name: ')
                print('VIN: {}'.format(vehicle.vin))
                print(json.dumps(vehicle.state.attributes[field], indent=4))
            else:
                print('No vehicle selected.')
           
        printmenu()
        choice=input("Type an option ")
        print()
        
    with open(configfilename, 'w') as configfile:
        config.write(configfile)

def light_flash(vehicle) -> None:
    """Trigger the vehicle to flash its lights."""
    status = vehicle.remote_services.trigger_remote_light_flash()
    print(status.state)

def sound_horn(vehicle) -> None:
    """Trigger the vehicle to sound its horn."""
    vehicle.remote_services.trigger_remote_horn()
    
def quick_status(vehicle) -> None:
    print('vehicle status: ')
    print('VIN: {}'.format(vehicle.vin))
    if not vehicle.has_check_control_messages:
        print('No check control messages')
    if vehicle.state.all_lids_closed and vehicle.state.all_windows_closed and (vehicle.state.door_lock_state.name in ['LOCKED','SECURED']) and vehicle.state.are_all_cbs_ok:
        print('Everything\'s OK')
    else:
        print('Something\'s open or unlocked!')
        if not vehicle.state.all_lids_closed:
            print('Following lids open: {}'.format(','.join([lid.name for lid in vehicle.state.open_lids])))
        if not vehicle.state.all_windows_closed:
            print('Following {} windows open: {}'.format(len(vehicle.state.open_windows),','.join([lid.name for lid in vehicle.state.open_windows])))
        if not vehicle.state.door_lock_state in ['LOCKED','SECURED']:
            print('Lock state {}'.format(vehicle.state.door_lock_state))

    
def printmenu() -> None:
    print()
    print('0. Select region')
    print('1. Enter Username')
    print('2. Enter my location')
    print('3. Select vehicle')
    print('4. Get status')
    print('5. Flash Lights')
    print('6. Honk horn')
    print('7. Get position')
    print('8. Lock doors')
    print('9. Unlock doors')
    print('a. Climatize (air condition or ventilate)')
    print('o. Open a Different Account')
    print('r. Spew raw status')
    print('i. Inquire status item (expert function)')
    print('q. Quit');
    print()


if __name__ == '__main__':
    main()
