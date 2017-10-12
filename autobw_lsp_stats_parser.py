import _csv
import re,os


def filtering(s):
    rgx = '(pkt)|(Byte)|(pps)|(Bps)|(Util)|(Bw)|(Reserved)'
    rg = re.compile(rgx, re.DOTALL)
    if rg.match(s):
        return False
    else:
        return True

def main():

    re2 = '(P2)|(P3)'
    rg2 = re.compile(re2, re.DOTALL)
    ext = [".log", ".log.0",".log.1",".log.2",".log.3",".log.4",".log.5",".log.6",".log.7",".log.8"]
    filelist = os.listdir('.')
    for files in filelist:
        if files.endswith(tuple(ext)):
            with open('test.csv','a') as out_file, open(files,'r') as in_file:
                writer = _csv.writer(out_file)
                writer.writerow(['time','LSPName','LSPID_TUNNELID','packets','TotalMbits','PPS','Ratebps','UTIL%','RESVBW_mbps'])
                for line in in_file:
                    coulmns = line[:-1].split(' ')
                    coulmns = list(filter(None, coulmns))
                    coulmns[0] = ' '.join(coulmns[:3])
                    del coulmns[1:3]
                    if rg2.match(coulmns[1]):
                        coulmns = list(filter(filtering,coulmns))
                        coulmns[2] = ' '.join(coulmns[2:8])
                        del coulmns[3:8]
                        #if not(float(coulmns[7].strip("%")) == 0.00):
                        # Converting BytePerSecond to Bits Per Second
                        coulmns[4] = 8 * int(coulmns[4])
                        coulmns[6] = 8 * int(coulmns[6])
                        coulmns[8] = 8 * int(coulmns[8])
                        # Converting bps to Mbps
                        coulmns[4] = coulmns[4]/(1000000)
                        coulmns[6] = coulmns[6]/(1000000)
                        coulmns[8] = coulmns[8]/(1000000)
                        writer.writerow(coulmns)


if __name__ == "__main__":
    main()
