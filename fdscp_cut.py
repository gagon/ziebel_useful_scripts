
of = open('/mnt/A1-Data1/Data/US/CoP/Buck_Federal_17-5H/DAS/DAS_CP/BF_17_5H_PRO_2015.08.06.04.04.17.fds','wb')
begin = 'FDS_Version = 1\nHeaderSize_Bytes = 23239'

offset = 56
total = 268435802823
remaining = total - offset
chunksize = 65536*1000
numblocks = remaining / chunksize
rest = remaining % chunksize
print(begin)
with open('/media/ziebel/USDAS_024/BUCK_FEDERAL/BF_17_5H_PRO_2015.08.06.04.04.17.fds','rb') as f:
    of.write(begin)
    f.seek(offset)
#    for i in range(numblocks):
    for i in range(numblocks-80):
        print('block ' + str(i) + ' of ' + str(numblocks))
        of.write(f.read(chunksize))
#    of.write(f.read(rest))

of.close()
f.close()
