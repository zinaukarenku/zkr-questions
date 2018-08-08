from .models import Politician, Area, Expert
import csv

def parse_vm(filename, party):
    with open('/home/zinaukarenku/'+filename+'.csv', "r") as infile:
        reader = csv.reader(infile, delimiter=",")
        for row in reader:
            try:
                if row[0]:
                    area = Area.objects.get(map_name=row[0])
                else:
                    area = Area.objects.get(map_name="Daugiamandatė")
                full_name = row[1]
                email = row[2]
                pol = Politician(full_name=full_name,email=email,party=party,area=area)
                pol.save()
            except Exception as e:
                print(row[1], e)

def parse_ex(filename):
    with open('/home/zinaukarenku/'+filename+'.csv', "r") as infile:
        reader = csv.reader(infile, delimiter=",")
        for row in reader:
            try:
                ex = Expert(full_name=row[1],email=row[2],organisation=row[1])
                ex.save()
            except Exception as e:
                print(row[1], e)
