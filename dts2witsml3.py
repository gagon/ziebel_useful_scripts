from lxml import etree
import datetime
import sys
import os


dtssys_uid = '0A-34-DA-66-1A-FE'
installedsystemname = 'DTS-1'
fiber_uid = '1'
fiber_name = 'ZF-01'


def addsimpletag(parent,name,value,**kwargs):
    e = etree.SubElement(parent,name,**kwargs)
    e.text = value
    return e

def addlogcurveinfo(parent,mnemonic,unit, curvedescription, uid):
    e = etree.SubElement(parent,'logCurveInfo',uid=uid)
    addsimpletag(e,'mnemonic',mnemonic)
    addsimpletag(e,'unit',unit)
    addsimpletag(e,'curveDescription', curvedescription)

def addblockcurveinfo(parent,curveId,columnIndex):
    e = etree.SubElement(parent,'blockCurveInfo')
    addsimpletag(e,'curveId', curveId)
    addsimpletag(e,'columnIndex',columnIndex)

def dts2witsml(inpath,outdir,welluid,fibermode):
    print(inpath,outdir)
    with open(inpath) as f:
        t = f.read().split('\n')
        hdr = t[0:13]
        data = t[13:]
        creationdate = \
                       datetime.datetime.\
                       strptime(hdr[8][11:].strip(),
                                '%Y/%m/%d %H:%M:%S')
    creationdate_out = str(creationdate.strftime('%Y-%m-%dT%H:%M:%S')) + '+04:00'
    creationdate_uid = str(creationdate.strftime('%Y%m%d%H%M%S'))


    #xsd='http://www.w3.org/2001/XMLSchema'
    #xmlns="http://www.witsml.org/schemas/131"
    #xsi="http://www.w3.org/2001/XMLSchema-instance"

    #version="1.3.1.1"
    #ns = "{xsi}"
    #root = etree.Element("WITSMLComposite",
    #                     version=version, 
    #                     nsmap={'xsi':xsi, 'xsd':xsd}
    #                 )
    #xmlns:witsml="http://www.witsml.org/schemas/131" 
    #xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    #root = etree.Element("WITSMLComposite", version=version)

    #root.set('{%s}witsml' % 'http://www.w3.org/2001/XMLSchema-instance', xmlns)
    #root.set('{%s}noNameSpaceSchemaLocation' % xsi,'http://www.witsml.org/schemas/131/WITSML_composite.xsd')

    #root.set('{%s}noNameSpaceSchemaLocation' % 'xsi','http://www.witsml.org/schemas/131/WITSML_composite.xsd')


    version="1.3.1.1"
    xsi="http://www.w3.org/2001/XMLSchema-instance"

    root = etree.Element("WITSMLComposite",
                         version=version, 
                         nsmap={'xsi':xsi,'witsml':'http://www.witsml.org/schemas/131'}
                     )
    root.set('{%s}noNameSpaceSchemaLocation' % xsi,'http://www.witsml.org/schemas/131/WITSML_composite.xsd')


    well = etree.SubElement(
        etree.SubElement(
            root,'wellSet'
        ),
        'well',
        uid=welluid
    )
    addsimpletag(well,'name',welluid)
    wellboreset = etree.SubElement(
        etree.SubElement(well,
                         'wellboreSet'
                     ),
        'wellbore',
        uid=welluid
    )
    addsimpletag(wellboreset,'name',welluid)
    dtsInstalledSystem = etree.SubElement(
        etree.SubElement(
            wellboreset,
            'dtsInstalledSystemSet'
        ),'dtsInstalledSystem', uid = dtssys_uid
    )
    addsimpletag(dtsInstalledSystem,'name',installedsystemname)
    fiber = etree.SubElement(
        etree.SubElement(
            dtsInstalledSystem,
            'fiberInformation'
        ),'fiber',uid=fiber_uid
    )
    addsimpletag(fiber,'name',fiber_name)
    addsimpletag(fiber,'mode',fibermode)
    dtsMeasurement = etree.SubElement(
        etree.SubElement(
            wellboreset,
            'dtsMeasurementSet'
        ),
        'dtsMeasurement',
        uid=':'.join([welluid,creationdate_uid])
    )

    wellinlog_uidref = ':'.join([welluid, installedsystemname])
    wellinlog_name = ':'.join([welluid, installedsystemname, fiber_uid, creationdate_uid])
    addsimpletag(dtsMeasurement,'name',' '.join([welluid,creationdate_out]))
    addsimpletag(dtsMeasurement,'installedSystemUsed', installedsystemname, uidRef=dtssys_uid)
    addsimpletag(dtsMeasurement,'dataInWellLog',wellinlog_name, uidRef = wellinlog_uidref)
    addsimpletag(dtsMeasurement,'connectedToFiber', fiber_name, uidRef = fiber_uid)

    wellLog = etree.SubElement(
        etree.SubElement(
            wellboreset,
            'wellLogSet'
        ),
        'wellLog',
        uid = wellinlog_uidref
    )
    addsimpletag(wellLog,'name', wellinlog_name)
    addsimpletag(wellLog,'serviceCompany','Ziebel AS')
    addsimpletag(wellLog,'creationDate',creationdate_out)
    addsimpletag(wellLog,'indexType','length')
    addsimpletag(wellLog,'nullValue','NULL')
    
    addlogcurveinfo(wellLog,'LENGTH','m','Length along the fiber - (Metres)','1')
    addlogcurveinfo(wellLog,'Temperature','degC','Temperature in degree celcius ', '2')
    #addlogcurveinfo(wellLog,'Stokes','Count','3')
    #addlogcurveinfo(wellLog,'Anti_Stokes','Count','4')
    #addlogcurveinfo(wellLog,'Reverse_Stokes','Count','5')
    #addlogcurveinfo(wellLog,'Reverse_Anti_Stokes','Count','6')
    
    blockInfo = etree.SubElement(wellLog,'blockInfo', uid='1')
    addsimpletag(blockInfo,'indexType','length')
    addsimpletag(blockInfo,'direction','increasing')
    addsimpletag(blockInfo,'indexCurve','LENGTH',columnIndex='1')
    
    addblockcurveinfo(blockInfo,'1','1')
    addblockcurveinfo(blockInfo,'2','2')
    #addblockcurveinfo(blockInfo,'3','3')
    #addblockcurveinfo(blockInfo,'4','4')
    #addblockcurveinfo(blockInfo,'5','5')
    #addblockcurveinfo(blockInfo,'6','6')
    
    logData = etree.SubElement(wellLog,'logData')
    for d in data:
        if '\t' in d:
            addsimpletag(logData, 'data',d.replace('\t',','),id='1')
        
    doc = etree.ElementTree(root)

    def swapstrings(a, b, c):
        '''
        swap the 2 substrings a and b in the string c
        '''
        return c.replace(a,'$$tmp$$').replace(b,a).replace('$$tmp$$',b)

    xml = etree.tostring(doc, xml_declaration=True, encoding='utf-8', pretty_print=True).decode('utf-8')
    # Due to a client erronous and pedantic implementation of witsml we must force the order of the attributes.
    xml = swapstrings('xmlns:witsml="http://www.witsml.org/schemas/131"', 'version="1.3.1.1"', xml)
    xml = swapstrings('version="1.3.1.1"', 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', xml)
    xml = swapstrings('xmlns:witsml="http://www.witsml.org/schemas/131"', 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', xml)

    fn = os.path.join(outdir,welluid + '_' + creationdate_out.replace(':','_') + '.witsml')
    with open(fn, 'wb') as outFile:
        print(xml[:300].encode('utf-8'))
        outFile.write(xml.encode('utf-8'))

    #print(etree.tostring(root, pretty_print=True).decode('utf-8'))
    
    # Save to XML file
    #outFile = open(outdir + '\\' + welluid + '_' + creationdate_out.replace(':','_') + '.witsml', 'wb')
    #outFile = open(os.path.join(outdir,welluid + '_' + creationdate_out.replace(':','_') + '.witsml'), 'wb')
    #doc.write(outFile, xml_declaration=True, encoding='utf-8') 

if __name__ == '__main__':
    import sys
    welluid = input('Enter the wellname: ')
    DTSpath = input('Enter the path of the .dts files: ')
    #welluid = "F-232"
    #DTSpath = r'F:\F232_cal_dts'
    fibermode = 'multimode'
    WMLPath = os.path.join(DTSpath,'_witsml')
    if not os.path.exists(WMLPath):
        os.makedirs(WMLPath)
    
#    print 'indir:', DTSpath
#    print 'outdir:', WMLPath
    for root, dirs, files in os.walk(DTSpath):
        for f in files:
            if f.endswith('.dts'):
                outdir = WMLPath+root[len(DTSpath):]
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                infile = os.path.join(root,f)
                #infile = '\\'.join((root,f))
                #outfile = '\\'.join((WMLPath,f))
                dts2witsml(infile,outdir,welluid,fibermode)
				
				
