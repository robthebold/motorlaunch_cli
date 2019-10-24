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
#import geocoder
import configparser
import getpass
import webbrowser
from  maps import map1, map2, map3
#document this pre-req
#import xdg
from pathlib import Path
from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name, valid_regions, Regions
from bimmer_connected.vehicle import VehicleViewDirection, PointOfInterest

def main() -> None:
    """Main function."""

    print()
    print('Motorlaunch, Copyright (C) 2019 Robert Bruce.')
    print('A text mode interface to the bimmer_connected library,')
    print('this program provides access to services and information')
    print('from BMW ConnectedDrive.')
    print()


    username, regionname, vin, browsername = read_config()

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
                    regionname = region_name.lower()
        if choice == '1':
            print('Current username: {}'.format(username))
            username = input("Type your new username ")
        if choice == '2':
            print('Paste a google maps URL, or')
            gps_position = parse_coordinates(input('enter lat, long in decimal format: '))
            print('Lat {}, Lon {}'.format(gps_position[0],gps_position[1]))
            if vehicle:
                vehicle.set_observer_position(gps_position[0],gps_position[1])
            poi = PointOfInterest(gps_position[0],gps_position[1])
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
                vin = vehicle.vin
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
            if vehicle:
                light_flash(vehicle)
            else:
                print('No vehicle selected.')
        if choice == '6':
            if vehicle:
                sound_horn(vehicle)
            else:
                print('No vehicle selected.')
        if choice == '7':
            if vehicle and vehicle.state.is_vehicle_tracking_enabled:
                print('Latitude {}, Longitude {}'.format(vehicle.state.gps_position[0],vehicle.state.gps_position[1]))
                send = input('Send to Pure Maps? ')
                if send == 'y' or send == 'Y':
                    mapper = 'harbour-pure-maps'
                    command = '{} geo:{},{} &'.format(mapper, vehicle.state.gps_position[0],vehicle.state.gps_position[1])
                    os.system(command)
            else:
                print('I\'m sorry Dave, I\'m afraid I can\'t do that.')
        if choice == '8':
            vehicle.remote_services.trigger_remote_door_lock()
        if choice == '9':
            vehicle.remote_services.trigger_remote_door_unlock()
        if choice == 'a':
            vehicle.remote_services.trigger_remote_air_conditioning()
        if choice == 'b':
            browsername = input('Please enter the executable name of your browser ')
        if choice == 'c':
            # Electric drivetrain only
            vehicle.remote_services.trigger_remote_charge_now()
        if choice == 'd':
            #Send a POI to car
            print('Paste a google maps URL, or')
            gps_position = parse_coordinates(input('Enter lat, long in decimal format, e.g. 34.01234, -92.98765 : '))
            print('Lat {}, Lon {}'.format(gps_position[0],gps_position[1]))
            poiname = input('Name this destination or hit <Enter> for none: ')
            streetname = input('Enter address or hit <Enter> for none: ')
            cityname = input('Enter city. <Enter> for none: ')
            zip = input('Enter postal (ZIP) code. <Enter> for none: ')
            countryname = input('Enter country name. <Enter> for none: ')
            if vehicle:
                poi = PointOfInterest(gps_position[0],gps_position[1],name=poiname, street=streetname, city=cityname, postalcode=zip)
                vehicle.send_poi(poi)
        if choice == 'l':
            # Get last trip statistics
            print('Last trip statistics:')
            print(json.dumps(vehicle.get_vehicle_lasttrip(),indent=4))
        if choice == 'm':
            if browsername != '':
                print('Range Map:')
                maps = vehicle.get_vehicle_rangemap()
                #if sort_keys then rangemaps are sorted by "type"
                print('The following rangemaps are available')
                i=1
                for map in maps['rangemaps']:
                    print('{} {}'.format(i,map['type']))
                    i +=1
                i=int(input('Select a rangemap: '))
                map = maps['rangemaps'][i-1]['polyline']
                f= open("rangemap.html","w+")
                f.write(map1)
                f.write('center: [{}, {}],'.format(maps["center"]["lon"],maps["center"]["lat"]))
                f.write(map2)
                firstline = True
                for point in map:
                    if  not firstline:
                        f.write(',')
                    f.write('[{}, {}]'.format(point['lon'], point['lat']))
                    firstline = False
                f.write(map3)
                f.close()
                #input('Press Enter')
                #browser = 'sailfish-browser'
                #command = '{} {} &'.format(browsername, f.name)
                #os.system(command)
                webbrowser.open(f.name)
                #print(json.dumps(maps,sort_keys=True,  indent=4)) #['rangemaps'][1]
            else:
                print('Enter your browser\'s executable name first. ')
        if choice == 'n':
            # Get destinations
            print('Vehicle destinations:')
            print(json.dumps(vehicle.get_vehicle_destinations(),indent=4))

        if choice == 's':
            # Get all trip statistics
            print('All trip statistics:')
            print(json.dumps(vehicle.get_vehicle_alltrips(),indent=4))

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
        if choice == 'p':
            if vehicle:
                index = 1
                while index != 0:
                    views = []
                    for view in VehicleViewDirection:
                        print('{} {}'.format(index,view.name))
                        views.append(view.name)
                        index +=1
                    index = int(input('Please select view or type 0 for done. '))
                    if index != 0:
                        print('{}'.format(views[index-1]))
                        get_image(vehicle,VehicleViewDirection(views[index-1]))
                        index = 1
            else:
                print('No vehicle selected - select one first')
        if choice =='r':
            if vehicle:
                print('Raw status info (You asked for it):')
                print('VIN: {}'.format(vehicle.vin))
                print(json.dumps(vehicle.state.attributes, indent=4))
            else:
                print('No vehicle selected.')

        if choice == 'w':
            # Get weekly charging planner
            print('Charging profile:')
            print(json.dumps(vehicle.get_vehicle_charging_profile(),indent=4))
        if choice == 'z':
            # Send message to car
            subject = input('Type the subject: ')
            message = input('Type your message ')
            vehicle.send_message(message,subject)
        if choice =='i':
            if vehicle:
                print('Inquire a single status field:')
                field=input('Carefully type exact field name: ')
                print('VIN: {}'.format(vehicle.vin))
                print(json.dumps(vehicle.state.attributes[field], indent=4))
            else:
                print('No vehicle selected.')
        if choice =='?':
           print_about()

        printmenu()
        choice=input("Type an option ")
        print()

    write_config(username, regionname, vin, browsername)

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


def get_image(vehicle, direction: VehicleViewDirection) -> None:
    """Download a rendered image of vehicle from direction point of view"""
    # NB FRONT and FRONTSIDE and also REAR and REARSIDE appear to be the same image
    # NB REARBIRDSEYE doesn't seem to be supported (at least for my car) do not use or crash
    print('Getting rendered image . . .');
    home = str(Path.home())
    datadir = home+'/.local/share/motorlaunch'
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    filename = datadir+'/image_'+vehicle.vin+'_'+direction.name+'.png'
    with open(filename, 'wb') as output_file:
        image_data = vehicle.get_vehicle_image(400,400,direction)
        output_file.write(image_data)
    print('Vehicle image saved to {}'.format(filename))
    
def parse_coordinates(coords_string) -> (float, float):
    """Process a string containing gps coordinates either in a URL or by themselves"""
    if "@" in coords_string and "google.com" in coords_string:
        #assume google maps url -- attempt a very naive parse
        coords_string,lonstring = coords_string.rsplit('!4d',1)
        #print('Longitude string is: {}'.format(lonstring))
        #print('Coordinates string is now: {}'.format(coords_string))
        other_stuff, latstring = coords_string.rsplit('!3d',1)
        #print('Latitude string is: {}'.format(latstring))
        #print('Other stuff is: {}'.format(other_stuff))
    #print(latstring, lonstring)
    if "geo:" in coords_string:
        #assuem this is a geocode
        other_stuff,coords_string = coords_string.rsplit('geo:',1)
        coords_string,other_stuff =  coords_string.rsplit('plus code:')
        latstring,lonstring = coords_string.split(',')
    else:
        latstring,lonstring = coords_string.split(',')
    lat=float(latstring)
    lon=float(lonstring)
    return lat,lon

def read_config() -> None:
    home = str(Path.home())
    configdir = home+'/.config/motorlaunch'
    configfilename = configdir+'/motorlaunch.ini'

    config = configparser.ConfigParser()
    config['credentials'] = {'username': ''}
    config['region'] = {'region': 'nowhere'}
    config['language'] = {'language':'en_us'}
    config['vehicles'] = {'currentvin': ''}
    config['browser'] = {'name':''}
    #Create config file directory if it doesn't already exist
    if not os.path.exists(configdir):
        os.mkdir(configdir)

    config.read(configfilename);
    username = config.get("credentials", "username")
    regionname = config.get('region','region')
    vin = config.get('vehicles','currentvin')
    browser = config.get('browser','name')
    #mapper = config.get('mapper','name')
    return username, regionname, vin, browser

def write_config(username, regionname, vin, browser) -> None:
    home = str(Path.home())
    configdir = home+'/.config/motorlaunch'
    configfilename = configdir+'/motorlaunch.ini'

    config = configparser.ConfigParser()
    config['credentials'] = {'username': ''}
    config['region'] = {'region': 'nowhere'}
    config['language'] = {'language':'en_us'}
    config['vehicles'] = {'currentvin': ''}
    config['browser'] = {'name':''}
    config['credentials']['username'] = username
    config['region']['region'] = regionname
    config['vehicles']['currentvin'] = vin
    config['browser']['name'] = browser

    with open(configfilename, 'w') as configfile:
        config.write(configfile)


def print_about() -> None:
    print()
    print('Motorlaunch, Copyright (C) 2019 Robert Bruce.')
    print('A text mode interface to the bimmer_connected library,')
    print('this program provides access to services and information')
    print('from BMW ConnectedDrive.')
    print()
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
    input('Press <Enter> to continue')
    print()


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
    print('c. Charge now (electric only)')
    print('d. Enter a new destination (POI)')
    print('l. Last trip statistics (electric?)')
    print('m. Range Map (electric?)')
    print('n. Destinations list')
    print('o. Open a Different Account')
    print('p. Get rendered image of vehicle')
    print('r. Spew raw status')
    print('s. All statistics (electric?)')
    print('w. Weekly charging schedule')
    print('z. Send message to car')
    print('i. Inquire status item (expert function)')
    print('?. About MotorLaunch')
    print('q. Quit');
    print()


if __name__ == '__main__':
    main()
