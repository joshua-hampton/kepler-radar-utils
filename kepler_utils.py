#!/usr/bin/env python
# coding: utf-8

# ==========================================================================
# Module for processing mmclx radar files from Kepler (MIRA-35) radar
# Author: Chris Walden, UK Research & Innovation and
#                       National Centre for Atmospheric Science
# Last modified: 20-02-2023
# ==========================================================================

"""Module for processing mmclx radar data from Kepler (MIRA-35) radar."""

module_version = 0.1;

import datetime

import netCDF4 as nc4
import numpy as np

from pyart.config import FileMetadata, get_fillvalue
from pyart.core.radar import Radar
from pyart.io.common import _test_arguments, make_time_unit_str

import yaml

from io import StringIO



def read_mira35_mmclx(filename, **kwargs):
    """
    Read a netCDF mmclx file from MIRA-35 radar.

    Parameters
    ----------
    filename : str
        Name of mmclx netCDF file to read data from.

    Returns
    -------
    radar : Radar
        Radar object.
    """

    # time, range, fields, metadata, scan_type, latitude, longitude, altitude, altitude_agl,
    # sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index, sweep_end_ray_index, rays_per_sweep,
    # target_scan_rate, rays_are_indexed, ray_angle_res,
    # azimuth, elevation, gate_x, gate_y, gate_z, gate_longitude, gate_latitude, projection, gate_altitude,
    # scan_rate, antenna_transition, 
    # None rotation, tilt, roll, drift, heading, pitch
    # ?? georefs_applied
    # instrument_parameters
    # radar_calibration
    # OK ngates
    # OK nrays
    # OK nsweeps
    
    # The following are not required for a fixed platform
    rotation = None;
    tilt = None;
    roll = None;
    drift = None;
    heading = None;
    pitch = None;
    georefs_applied = None;
    antenna_transition = None;
     
    # -------------------------
    # test for non empty kwargs
    # -------------------------
    _test_arguments(kwargs)

    # --------------------------------
    # create metadata retrieval object
    # --------------------------------
    filemetadata = FileMetadata('mmclx')

    # -----------------
    # Open netCDF4 file
    # -----------------
    ncobj = nc4.Dataset(filename)
    nrays = len(ncobj.dimensions["time"])
    ngates = len(ncobj.dimensions["range"])
    nsweeps = 1; # We only have single sweep files 
    
    ncvars = ncobj.variables

    # --------------------------------
    # latitude, longitude and altitude
    # --------------------------------
    latitude = filemetadata('latitude')
    longitude = filemetadata('longitude')
    altitude = filemetadata('altitude')

    z = StringIO(ncobj.getncattr('Latitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['lat','zs2'])
    if z1['zs2']==b'S' and z1['lat']>0: 
        latitude['data'] = -z1['lat']
    else:
        latitude['data'] = z1['lat']  
        
    z = StringIO(ncobj.getncattr('Longitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['lon','zs2'])
    
    if z1['zs2']==b'W' and z1['lon']>0: 
        longitude['data'] = -z1['lon']
    else:
        longitude['data'] = z1['lon']  
    
    z = StringIO(ncobj.getncattr('Altitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['alt','zs2'])
    altitude['data'] = z1['alt']

    # Original mmclx metadata
    # -----------------------
    # convention: "CF-1.0"
    # location: "Chilbolton"
    # Altitude:
    # Latitude:
    # Longitude:
    # system: "B3XC"
    # title: "MIRA Cloud Radar Data"
    # institution: "National Centre for Atmospheric Science (NCAS)"
    # source: "220520_101223.pds"
    # reference: "Ka Band Cloud Radar MIRA 35, METEK GmbH www.metek.de"

    # Most important information from the header structure
    # ----------------------------------------------------
    # nfft: "number_of_fft_points"
    # NyquistVelocity: 
    # nave: "number_of_spectral_averages"
    # ovl: "overlapping_ffts_flag"
    # zrg: "number_of_range_gates"
    # rg0: "number_of_lowest_range_gate"
    # drg: "range_resolution"
    # lambda: "wavelength"
    # range: "range_from_antenna_to_centre_of_each_range_gate"

    # Most important information from the SRVI struture given at each dwell time
    # ---------------------------------------------------------------------------
    # time: "seconds since 1970-01-01T00:00:00Z"
    # # microsec: 
    # tpow: "average_transmit_power"
    # npw1: "noise_power_co-channel"
    # npw2: "noise_power_cross-channel"
    # cpw1: "snr_of_calibration_signal_co-channel"
    # cpw2: "snr_of_calibration_signal_cross-channel"
    # grst: "general_radar_state"
    # azi: "azimuth"
    # elv: "elevation"
    # aziv: "azimuth_angle_velocity"
    # northangle: "north_angle"
    # elvv: "elevation_angle_velocity"
    # LO_Frequency: "transmit_frequency"
    # DetuneFine: "detuning_of_local_scillator_detected_from_Txn_footprint"

metadata_keymap = {
    "location": "platform",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "Altitude": "altitude",
    "system": "instrument_serial_nnmber",
    "title": "title",
    "institution": "institution",
    "reference": "reference",

}

 # time, range, fields, metadata, scan_type, latitude, longitude, altitude, altitude_agl,
    # sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index, sweep_end_ray_index, rays_per_sweep,
    # target_scan_rate, rays_are_indexed, ray_angle_res,
    # azimuth, elevation, gate_x, gate_y, gate_z, gate_longitude, gate_latitude, projection, gate_altitude,
    # scan_rate, antenna_transition, 
    # None rotation, tilt, roll, drift, heading, pitch
    # ?? georefs_applied
    # instrument_parameters
    # radar_calibration

 variables_keymap = {
        "Zg": "DBZH",
        "VELg": "VEL",
        "RMSg": "WIDTH",
        "LDRg": "LDR",
        "SNRg": "SNR",
        "elv": "elevation",
        "elvv": "elevation_angle_velocity"
        "azi": "azimuth_angle",
        "aziv": "azimuth_angle_velocity",
        "nfft": "nfft",
        "nave": "nave",
        "prf": "prf",
        "rg0": "rg0",
    }

variables = list(keymap.keys())

# SNRg, VELg, RMSg, LDRg, NPKg, SNRg
#RHO DPS PHOwav LDRnormal
# HSDco HSDcx Zg ISDRco ISDRcx 
# MRMco MRMcx RadarConst SNRCorFaCo SNRCorFaCx SKWg

    # Variables
    # nfft
    # prf
    # NyquistVelocity
    # nave
    
    # metadata
    #metadata = filemetadata("metadata")
    #metadata_mapping = {
    #    "vcp-value": "vcp",
    #    "radarName-value": "radar_name",
    #    "ConversionPlugin": "conversion_software",
    #}
    #for netcdf_attr, metadata_key in metadata_mapping.items():
    #    if netcdf_attr in dset.ncattrs():
    #        metadata[metadata_key] = dset.getncattr(netcdf_attr)

    # --------
    # metadata
    # --------
    metadata = filemetadata('metadata')
    for k in ['institution', 'title', 'used_algorithms']:
        if k in ncobj.ncattrs(): 
            metadata[k] = ncobj.getncattr(k)

    metadata['instrument_name']='ncas-radar-mobile-ka-band-1'

    # ------------------------------------------
    # sweep_start_ray_index, sweep_end_ray_index
    # ------------------------------------------
    sweep_start_ray_index = filemetadata("sweep_start_ray_index")
    sweep_end_ray_index = filemetadata("sweep_end_ray_index")
    sweep_start_ray_index["data"] = np.array([0], dtype="int32")
    sweep_end_ray_index["data"] = np.array([nrays - 1], dtype="int32")

    # ------------
    # sweep number
    # ------------
    sweep_number = filemetadata("sweep_number")
    sweep_number["data"] = np.array([0], dtype="int32")

    # -----------------------
    # sweep_mode, fixed_angle
    # -----------------------
    sweep_modes = {'ppi' : 'ppi', 'rhi' : 'rhi','vert' : 'vertical_pointing','man' : 'manual_rhi'}

    sweep_mode = filemetadata("sweep_mode")

    print(filename.lower());

    scan_type = None;
    sweep_mode["data"] = np.array(1 * [None]);

    for key, value in sweep_modes.items():
        print(key)
        if key in filename.lower(): 
            scan_type = value;
            sweep_mode["data"] = np.array(1 * [value]);
            sweep_mode["data"][0] = value;
            break;

    fixed_angles = {'ppi' : ncvars['elv'][0], 'rhi' : ncvars['azi'][0], 'vertical_pointing' : ncvars['elv'][0], "manual_rhi" : ncvars['azi'][0]}

    fixed_angle = filemetadata("fixed_angle")

    if scan_type is not None:
        fixed_angle["data"] = np.array(1 * [fixed_angles[scan_type]])
    else:
        fixed_angle["data"] = np.array(1 * [None])


    # time
    # interpolate between the first and last timestamps in the Time variable
    time = filemetadata('time')
    nctime = ncvars['time']
    
    dtime = nc4.num2date(ncvars['time'][:],'seconds since 1970-01-01 00:00:00')

    for idx, x in np.ndenumerate(dtime):
        dtime[idx]=x.replace(microsecond=ncvars['microsec'][idx])
            
    base_time = dtime[0].replace(hour=0, minute=0, second=0, microsecond=0)
    
    time['units'] = make_time_unit_str(base_time)  
    time['data']  = nc4.date2num(dtime,time['units']);

    # range
    _range = filemetadata('range')
    _range['data'] = ncvars['range'][:]
    _range['metres_to_centre_of_first_gate'] = _range['data'][0]
    # assuming the distance between all gates is constant, may not
    # always be true.
    _range['metres_between_gates'] = (_range['data'][1] - _range['data'][0])

    # azimuth, elevation
    azimuth = filemetadata('azimuth')
    elevation = filemetadata('elevation')

    azimuth['data'] = ncvars['azi'][:]
    elevation['data'] = ncvars['elv'][:]


    metadata['time_coverage_start'] = datetime.strftime(dtime[0],'%Y-%m-%dT%H:%M:%SZ');
    metadata['time_coverage_end'] = datetime.strftime(dtime[-1],'%Y-%m-%dT%H:%M:%SZ');


    # fields
    # mmclx files contain the following: 
    # where x="g" (global),"" (hydrometeors),"plank" (plankton),"rain","cl" 
    # SNRx 
    # VELx
    # RMSx
    # LDRx
    # LWC (liquid water content of peaks classified as rain)
    # RR (rain rate of peaks classified as rain)
    # Ze (equivalent radar reflectivity of all hydrometeors)
    # Zg (equivalent radar relectivity of all targets (global))
    # Z (similer to Ze but with Mie correction applied, and a pressure and temperature dependent value of |Kw|^2
    # MeltHeiDet (melting layer height detected from LDR if detected, else -1)
    # MeltHeiDb (melting layer height as deduced from external sources)
    # MeltHei (melting layer height from both sources)
    # TEMP (temperature profile faked form external sources)
    # ISDRco (ratio between power integrated over the largest peak and the noise level - to indicate saturation)
    # ISDRcx (cross-polar channel version of ISDRco)
    # RadarConst (radar constant related to 5km range, Zx = RadarCponst*SNRx*(range/5 km)^2), with range at the centre of each range gate)
    # SNRCorFaCo ()
    # SNRCorFaCx ()
    # 
    #field_name = ncobj.TypeName

    #field_data = np.ma.array(dset.variables[field_name][:])
    #if "MissingData" in dset.ncattrs():
    #    field_data[field_data == dset.MissingData] = np.ma.masked
    #if "RangeFolded" in dset.ncattrs():
    #    field_data[field_data == dset.RangeFolded] = np.ma.masked

    fields = {}
    #fields = {field_name: filemetadata(field_name)}
    #fields[field_name]["data"] = field_data
    #fields[field_name]["units"] = dset.variables[field_name].Units
    #fields[field_name]["_FillValue"] = get_fillvalue()


    try:
        ncvars['Zg']
        field_name = filemetadata.get_field_name('Zg')
        field_dic = filemetadata(field_name)
        #field_dic['_FillValue'] = ncvars['Zg']._FillValue
        field_dic['units'] = ncvars['Zg'].units
        field_dic['data'] = 10.0*np.log10(ncvars['Zg'][:]);
        #field_dic['applied_calibration_offset'] = ncvars['ZED_HC'].applied_calibration_offset
        fields[field_name] = field_dic
    except KeyError:
        print("Zg does not exist")

    if "Zg" in ncvars:
        field_name = filemetadata.get_field_name('Zg')
        field_dic = filemetadata(field_name)
        #field_dic['_FillValue'] = ncvars['Zg']._FillValue
        field_dic['units'] = ncvars['Zg'].units
        field_dic['data'] = 10.0*np.log10(ncvars['Zg'][:]);
        #field_dic['applied_calibration_offset'] = ncvars['ZED_HC'].applied_calibration_offset
        fields[field_name] = field_dic
    except KeyError:
        print("Zg does not exist")



    # instrument_parameters
    instrument_parameters = {}

    radar_calibration = {}


    #if "PRF-value" in dset.ncattrs():
    #    dic = filemetadata("prt")
    #    prt = 1.0 / float(dset.getncattr("PRF-value"))
    #    dic["data"] = np.ones((nrays,), dtype="float32") * prt
    #    instrument_parameters["prt"] = dic

    #if "PulseWidth-value" in dset.ncattrs():
    #    dic = filemetadata("pulse_width")
    #    pulse_width = dset.getncattr("PulseWidth-value") * 1.0e-6
    #    dic["data"] = np.ones((nrays,), dtype="float32") * pulse_width
    #    instrument_parameters["pulse_width"] = dic

    #if "NyquistVelocity-value" in dset.ncattrs():
    #    dic = filemetadata("nyquist_velocity")
    #    nyquist_velocity = float(dset.getncattr("NyquistVelocity-value"))
    #    dic["data"] = np.ones((nrays,), dtype="float32") * nyquist_velocity
    #    instrument_parameters["nyquist_velocity"] = dic

    #if "Beamwidth" in dset.variables:
    #    dic = filemetadata("radar_beam_width_h")
    #    dic["data"] = dset.variables["Beamwidth"][:]
    #    instrument_parameters["radar_beam_width_h"] = dic

    ncobj.close()

    return Radar(
        time,
        _range,
        fields,
        metadata,
        scan_type,
        latitude,
        longitude,
        altitude,
        sweep_number,
        sweep_mode,
        fixed_angle,
        sweep_start_ray_index,
        sweep_end_ray_index,
        azimuth,
        elevation,
        instrument_parameters=instrument_parameters,
        radar_calibration=radar_calibration
    )





def read_mmclx(filename, **kwargs):
    """
    Read a netCDF mmclx file from MIRA-35 radar.

    Parameters
    ----------
    filename : str
        Name of netCDF file to read data from.

    Returns
    -------
    radar : Radar
        Radar object.
    """
    # test for non empty kwargs
    _test_arguments(kwargs)

    # create metadata retrieval object
    filemetadata = FileMetadata('mmclx')

    # read the data
    ncobj = netCDF4.Dataset(filename)
    ncvars = ncobj.variables

    # general parameters
    nrays = ncvars['azi'].shape[0]
    scan_type = 'ppi'

    # time
    # interpolate between the first and last timestamps in the Time variable
    time = filemetadata('time')
    nctime = ncvars['time']
    
    dtime = nc4.num2date(ncvars['time'][:],'seconds since 1970-01-01 00:00:00')

    for idx, x in np.ndenumerate(dtime):
        dtime[idx]=x.replace(microsecond=ncvars['microsec'][idx])
            
    base_time = dtime[0].replace(hour=0, minute=0, second=0, microsecond=0)
    
    
    time['units'] = make_time_unit_str(base_time)  
    time['data']  = date2num(dtime,time['units']);

    # range
    _range = filemetadata('range')
    _range['data'] = ncvars['range'][:]
    _range['metres_to_centre_of_first_gate'] = _range['data'][0]
    # assuming the distance between all gates is constant, may not
    # always be true.
    _range['metres_between_gates'] = (_range['data'][1] - _range['data'][0])

    # fields
    # files contain a single corrected reflectivity field
    fields = {}
    
    try:
        ncvars['Zg']
        field_name = filemetadata.get_field_name('Zg')
        field_dic = filemetadata(field_name)
        #field_dic['_FillValue'] = ncvars['Zg']._FillValue
        field_dic['units'] = 'dBZ';
        field_dic['data'] = 10.0*np.log10(ncvars['Zg'][:]);
        #field_dic['applied_calibration_offset'] = ncvars['ZED_HC'].applied_calibration_offset
        fields[field_name] = field_dic
    except KeyError:
        print("Zg does not exist")
    
    try:
        ncvars['Zg']
        field_name = filemetadata.get_field_name('Zg')
        field_dic = filemetadata(field_name)
        #field_dic['_FillValue'] = ncvars['Zg']._FillValue
        field_dic['units'] = ncvars['Zg'].units
        field_dic['data'] = 10.0*np.log10(ncvars['Zg'][:]);
        #field_dic['applied_calibration_offset'] = ncvars['ZED_HC'].applied_calibration_offset
        fields[field_name] = field_dic
    except KeyError:
        print("Zg does not exist")

    # -----------------------------
    # latitude, longitude, altitude
    # -----------------------------
    latitude = filemetadata('latitude')
    longitude = filemetadata('longitude')
    altitude = filemetadata('altitude')
    
    # metadata
    metadata = filemetadata('metadata')
    for k in ['institution', 'title', 'used_algorithms']:
        if k in ncobj.ncattrs(): 
            metadata[k] = ncobj.getncattr(k)
    
    from io import StringIO

    z = StringIO(ncobj.getncattr('Latitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['lat','zs2'])
    if z1['zs2']==b'S' and z1['lat']>0: 
        latitude['data'] = -z1['lat']
    else:
        latitude['data'] = z1['lat']  
        
    z = StringIO(ncobj.getncattr('Longitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['lon','zs2'])
    
    if z1['zs2']==b'W' and z1['lon']>0: 
        longitude['data'] = -z1['lon']
    else:
        longitude['data'] = z1['lon']  
    
    z = StringIO(ncobj.getncattr('Altitude'))
    
    z1 = np.genfromtxt(z, dtype=None, names=['alt','zs2'])
    altitude['data'] = z1['alt']
    
    
    # sweep parameters
    # sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
    # sweep_end_ray_index
    sweep_number = filemetadata('sweep_number')
    sweep_mode   = filemetadata('sweep_mode')
    fixed_angle  = filemetadata('fixed_angle')
    sweep_start_ray_index = filemetadata('sweep_start_ray_index')
    sweep_end_ray_index   = filemetadata('sweep_end_ray_index')

    # We only store single sweeps 
    sweep_number['data'] = np.arange(1, dtype='int32')
    sweep_mode['data'] =  np.array(1 * ['sector'])  # THIS NEEDS TO BE DETERMINED

    fixed_angle['data'] = np.array([np.round(ncvars['elv'][0],2)], dtype='float32')#np.array([0], dtype='float32')
    sweep_start_ray_index['data'] = np.array([0], dtype='int32')
    sweep_end_ray_index['data'] = np.array([nrays-1], dtype='int32')

    # ------------------
    # azimuth, elevation
    # ------------------
    azimuth = filemetadata('azimuth')
    elevation = filemetadata('elevation')

    azimuth['data'] = ncvars['azi'][:]
    elevation['data'] = ncvars['elv'][:]#np.array([0.], dtype='float32')

 
    # ---------------------
    # instrument parameters
    # ---------------------
    instrument_parameters = None
    


    return Radar(
        time, _range, fields, metadata, scan_type,
        latitude, longitude, altitude,
        sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
        sweep_end_ray_index,
        azimuth, elevation, 
        instrument_parameters=instrument_parameters)

# ===================
# CONVERSION ROUTINES
# ===================

def convert_kepler_mmclx2l0b(infile,outfile,yaml_project_file,yaml_instrument_file,tracking_tag):

    """This routine converts mmclx data from the NCAS Mobile Ka-band Radar (Kepler) to Level 0b (cfradial) data.
    Metadata are added using information in two YAML files the yaml_project_file, and yaml_instrument_file.

    :param infile: Full path of NetCDF Level 0a mmclx data file, e.g. `<path-to-file>/20220907_071502.vert.mmclx`
    :type infile: str

    :param outfile: Full path of NetCDF Level 0b output file, e.g. `<path-to-file>/ncas-radar-mobile-ka-band-1_cao_20220907-071502_fix_l0b_v1.0.nc`
    :type outfile: str
    """
    instrument_tagname = "radar-kepler"

    # ---------------------------------------
    # Read metadata from YAML instrument file
    # ---------------------------------------  
    with open(yaml_instrument_file, "r") as stream:
        try:
            instruments = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for elem in instruments:
        if instrument_tagname in elem:
            instrument = elem[instrument_tagname];

    # -------------------------------------
    # Read metadata from YAML projects file
    # -------------------------------------  
    with open(yaml_project_file, "r") as stream:
        try:
            projects = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for p in projects:
        if tracking_tag in p:
            project = p[tracking_tag];

    radar = instrument["instrument_name"];

    for n in project["ncas_instruments"]:
        if radar in n:
            project_instrument = n[radar];

    print(project_instrument);
            
    
    RadarDataset = read_mira35_mmclx(infile);

    # Use PyART to create CfRadial file
    pyart.io.write_cfradial(outfile, RadarDataset, format='NETCDF4', time_reference=True)

    #DSin = nc4.Dataset(infile);

    #dt_start = cftime.num2pydate(DSin['time'][0],DSin['time'].units)
    #dt_end   = cftime.num2pydate(DSin['time'][-1],DSin['time'].units)

    # FIXME: need to add the microsecs which are stored separately in mmclx files

    # Should modify below to write to cfradial using pyart.
    # Then will modify the files to make them NCAS compliant.

    #try: outfile.close()  # just to be safe, make sure dataset is not already open.
    #except: pass
    #DSout = nc4.Dataset(outfile,mode='w',format='NETCDF4')
    #print("Creating {}".format(outfile));

    # -------------------------------------------------------
    # Read freshly created cfradial file to add NCAS metadata
    # -------------------------------------------------------
    DS = nc4.Dataset(outfile);

    DS.product_version = "v1.0" ;
    DS.processing_level = "0b" ;

    DS.licence = project["data_licence"];
    DS.acknowledgement = project["acknowledgement"];
    #DS.platform = "Chilbolton Atmospheric Observatory" ;
    #DS.platform_type = "stationary_platform" ;
    DS.title = ncas_instrument["title"];
    DS.creator_name = "Chris Walden" ;
    DS.creator_email = "chris.walden@ncas.ac.uk" ;
    DS.creator_url = "https://orcid.org/0000-0002-5718-466X" ;
    DS.institution = "National Centre for Atmospheric Science (NCAS)";
    DS.instrument_name = instrument["insstrument_name"];
    DS.instrument_software = "" ;
    DS.instrument_software_version = "" ;

    #DS.references = "";
    #DS.source = "NCAS Mobile Ka-band Radar (Kepler)";
    #DS.comment = "";
    DS.project = project["project_name"];
    DS.project_principal_investigator = project["principal_investigator"]["name"];
    DS.project_principal_investigator_email = project["principal_investigator"]["email"];
    DS.project_principal_investigator_url = project["principal_investigator"]["pid"];

    DS.processing_software_url = "";
    DS.processing_software_version = "";

    #DS.scantype = "vertical_pointing";

    DS.time_coverage_start = datetime.strftime(dt_start,'%Y-%m-%dT%H:%M:%SZ');
    DS.time_coverage_end = datetime.strftime(dt_end,'%Y-%m-%dT%H:%M:%SZ');
    #DS.geospatial_bounds = "51.1450N -1.4384E";

    
    # ----------------
    # Scalar variables
    # ----------------

    #varin = DSin['latitude'];
    #varout = DSout.createVariable('latitude',varin.datatype);
    #varout.standard_name = 'latitude';
    #varout.long_name = 'latitude of the antenna';
    #varout.units = 'degree_north';
    #varout[:]=51.1450;

    #varin = DSin['longitude'];
    #varout = DSout.createVariable('longitude',varin.datatype);
    #varout.standard_name = 'longitude';
    #varout.long_name = 'longitude of the antenna';
    #varout.units = 'degree_east';
    #varout[:]=-1.4384;

    #varin = DSin['height'];
    #varout = DSout.createVariable('altitude',varin.datatype);
    #varout.standard_name = 'altitude';
    #varout.long_name = 'altitude of the elevation axis above the geoid (WGS84)';
    #varout.units = 'm';
    #varout[:]=146.7;

    #varout = DSout.createVariable('altitude_agl',varin.datatype);
    #varout.standard_name = 'altitude';
    #varout.long_name = 'altitude of the elevation axis above ground';
    #varout.units = 'm';
    #varout[:]=16.0;

    #varin = DSin['frequency'];
    #varout = DSout.createVariable('frequency',varin.datatype);
    #varout.standard_name = 'radiation_frequency';
    #varout.long_name = 'frequency of transmitted radiation';
    #varout.units = 'GHz';
    #varout[:]=varin[:];

    #varin = DSin['prf'];
    #varout = DSout.createVariable('prf',varin.datatype);
    #varout.long_name = 'pulse repetition frequency';
    #varout.units = 'Hz';
    #varout[:]=varin[:];

    #varin = DSin['beamwidthH'];
    #varout = DSout.createVariable('beamwidthH',varin.datatype);
    #varout.long_name = 'horizontal angular beamwidth';
    #varout.units = 'degree';
    #varout[:]=varin[:];

    #varin = DSin['beamwidthV'];
    #varout = DSout.createVariable('beamwidthV',varin.datatype);
    #varout.long_name = 'vertical angular beamwidth';
    #varout.units = 'degree';
    #varout[:]=varin[:];

    #varin = DSin['antenna_diameter'];
    #varout = DSout.createVariable('antenna_diameter',varin.datatype);
    #varout.long_name = 'antenna diameter';
    #varout.units = 'm';
    #varout[:]=varin[:];

    #varin = DSin['pulse_period'];
    #varout = DSout.createVariable('pulse_width',varin.datatype);
    #varout.long_name = 'pulse width';
    #varout.units = 'us';
    #varout[:]=varin[:];

    #varin = DSin['transmit_power'];
    #varout = DSout.createVariable('transmit_power',varin.datatype);
    #varout.long_name = 'peak transmitted power';
    #varout.units = 'W';
    #varout[:]=varin[:];


    # ---------------
    # Field variables
    # ---------------
    # These are:
    # SNR, VEL, RMS, LDR, NPK, SNRg, VELg, NPKg, RHO, DPS, RHOwav, DPSwav, 
    # HSDco, HSDcx, Ze, Zg, ISDRco, ISDRcx
    # The ones to use are:
    # SNR, VEL, RMS, LDR, NPK, RHO, DPS, HSDco, HSDcx, Ze, ISDRco, ISDRcx


    # -----------------------
    # Update history metadata
    # -----------------------
    user = getpass.getuser()

    updttime = datetime.utcnow()
    updttimestr = updttime.ctime()

    history = updttimestr + (" - user:" + user
    + " machine: " + socket.gethostname()
    + " program: kepler_utils.convert_kepler_mmclx2l0b"
    + " version:" + str(module_version));

    DSout.history = history + "\n" + DSin.history;

    DSout.last_revised_date = datetime.strftime(updttime,'%Y-%m-%dT%H:%M:%SZ')

    DSin.close();
    DSout.close();

    return

def process_kepler(datestr,inpath,outpath,yaml_project_file,yaml_instrument_file,tracking_tag):

    pattern = '*{}*.mmclx'.format(datestr);

    print(datestr);
    print(inpath);
    datepath = os.path.join(inpath,datestr);

    tsfiles = [];
    tsdirs = [];

    for root,dirs,files in os.walk(datepath):
        tsfiles += [os.path.join(root,f) for f in fnmatch.filter(files, pattern)];
        tsdirs += dirs;

    data_version = "1.0";

    #dBZ_offset = 9.0;
    #range_offset = -865.56+864.0;

    l0bpath = os.path.join(outpath,'L0b',datestr);
    #l1path = os.path.join(outpath,'L1',datestr);

    os.makedirs(l0bpath,exist_ok=True);
    os.makedirs(l1path,exist_ok=True);

    print(tsdirs);
    for dir in tsdirs:
        print("I am Here!");
        os.makedirs(os.path.join(l0bpath,dir),exist_ok=True);
        #os.makedirs(os.path.join(l1path,dir),exist_ok=True);

    for f in tsfiles:
        outfile_splits = os.path.split(f);

        outfile_string = outfile_splits[1].replace('.mmclx','_l0b.nc');
        splits = outfile_string.split('_');
        instrument_name ='ncas-mobile-radar-ka-band-1';
        platform = 'cao';
        datestr = splits[1][0:8];
        timestr = splits[1][8:];
        level = splits[3].split('.')[0];
        l0bfile = '{}_{}_{}-{}_{}_{}_v{}.nc'.format(instrument_name,platform,datestr,timestr,splits[2],level,data_version)

        convert_kepler_mmclx2l0b(f,l0bfile,yaml_project_file,yaml_instrument_file,tracking_tag);

    return


# ------------------------------------------------------------------------
# Define function to produce cfradial files from mmclx files
# ------------------------------------------------------------------------
def mmclx_to_cfradial(mclxfile):

    user = getpass.getuser()

    print('Opening NetCDF file ' + mmclxfile)
    DS = nc4.Dataset(ncfile,'r+')

    scantype = DS.getncattr('scantype');

    dataset.close();

    # --------------------------------
    # Open NetCDF file using arm_pyart
    # --------------------------------
    if (scantype=='RHI'):
        radar = pyart.aux_io.read_camra_rhi(ncfile);
    elif (scantype=='PPI'):
        radar = pyart.aux_io.read_camra_ppi(ncfile);

    # -----------------------------------
    # Write cfradial file using arm_pyart
    # -----------------------------------
    cfradfile=ncfile.replace(".nc","-cfrad.nc");

    pyart.io.cfradial.write_cfradial(cfradfile, radar, format='NETCDF4',
        time_reference=False)
