def init_village_db():
    print("starting village creation")
    count = 0
    villages = []
    with open('../villages_list.csv','r',encoding="utf8") as file:
        reader = csv.reader(file)
        for row in reader:
            villages.append(row)
            count += 1
    print('completed csv read : ',count)
    print('creating database....')
    count = 0
    for i in range(1,len(villages)):
        villages[i] = villages[i][0].split(';')
        village = Village(
            village_id = villages[i][7],
            village_name = villages[i][9],
            district = villages[i][4],
            state = villages[i][2],
            pincode = 100,
            head_email = 'email id'
        )
        try:
            db.session.add(village)
            db.session.commit()
            count += 1
            if count%1000 == 0:
                print('[INFO] PROCCESSED :',count)
        except:
            print('already exists')
    print("added all villages")
