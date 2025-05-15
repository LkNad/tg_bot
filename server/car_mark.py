from deep_translator import GoogleTranslator

eng_marks = ["Abarth", "Acura", "Adler", "Aito", "Aiways", "Aixam",
             "Alfa Romeo", "Alpina", "Ambertruck", "Arcfox", "Aston Martin",
             "Audi", "Aurus", "Austin", "Avatr", "BAIC", "Bajaj", "BAW",
             "Belgee", "Bentley", "BMW", "Borgward", "Brilliance", "Bugatti",
             "Buick", "BYD", "Cadillac", "Changan", "Chery", "Chevrolet",
             "Chrysler", "Citroen", "Cupra", "Dacia", "Daewoo", "Daihatsu",
             "Daimler", "Datsun", "Dayun", "Delage", "Denza", "Derways",
             "Dodge", "Dongfeng", "Doninvest", "DS", "DW Hower", "Eagle",
             "Evolute", "Exeed", "Exlantix", "Facel Vega", "FAW", "Ferrari",
             "Fiat", "Fisker", "Ford", "Forthing", "Foton", "GAC", "GAC Aion",
             "GAC Trumpchi", "Geely", "Genesis", "Geo", "GMC", "Great Wall",
             "Hafei", "Haima", "Haval", "Hawtai", "HiPhi", "Honda", "Hongqi",
             "Horch", "Hozon", "Hummer", "Hyundai", "IM Motors (Zhiji)",
             "Infiniti", "Innocenti", "Iran Khodro", "Isuzu", "JAC", "Jaecoo",
             "Jaguar", "Jeep", "Jetour", "Jetta", "Jidu", "Kaiyi", "KGM", "Kia",
             "Knewstar", "Lada", "Lamborghini", "Lancia", "Land Rover",
             "Leapmotor", "Lexus", "Liebao Motor", "Lifan", "Lincoln", "Livan",
             "Lixiang", "Lotus", "Luxgen", "Lynk & Co", "M-Hero", "Maextro",
             "Maple", "Marussia", "Maserati", "Maxus", "Maybach", "Mazda",
             "McLaren", "Mercedes-Benz", "Mercury", "Metrocab", "MG", "Mini",
             "Mitsubishi", "Mitsuoka", "Nio", "Nissan", "Oldsmobile", "Omoda",
             "Opel", "Ora", "Oshan", "Oting", "Pagani", "Peugeot", "Plymouth",
             "Polar Stone (Jishi)", "Polestar", "Pontiac", "Porsche", "Proton",
             "Puch", "Ram", "Ravon", "Renault", "Renault Samsung",
             "Rising Auto", "Rivian", "Rolls-Royce", "Rover", "Rox", "Saab",
             "Saturn", "Scion", "SEAT", "Seres", "Skoda", "Skywell", "Smart",
             "Solaris", "Sollers", "Soueast", "SsangYong", "Stelato", "Steyr",
             "Subaru", "Suzuki", "SWM", "Tank", "Tatra", "Tesla", "Tianye",
             "Toyota", "Triumph", "TVR", "Volkswagen", "Volvo", "Vortex",
             "Voyah", "Wartburg", "Weltmeister", "Wey", "Willys", "Xcite",
             "Xiaomi", "Xin Kai", "Xpeng", "Zeekr", "Zotye", "ZX"]

ru_marks = ["Автокам", "ГАЗ", "ЗАЗ", "ЗИЛ", "ЗиС", "Иж", "ЛуАЗ", "Москвич",
            "СМЗ", "ТагАЗ", "УАЗ", "ВАЗ"]


def sercher(response):
    lower_ru_marks = list(map(lambda x: x.lower(), ru_marks))
    lower_eng_marks = list(map(lambda x: x.lower(), eng_marks))
    resp = response.lower()
    if resp == "lada" or resp == "ваз":
        return "Lada"
    elif resp in lower_ru_marks:
        return ru_marks[lower_ru_marks.index(resp)]
    elif resp in lower_eng_marks:
        return eng_marks[lower_eng_marks.index(resp)]
    else:
        response = (
            GoogleTranslator(source='ru', target='en').translate(response))
        if response.lower() in lower_eng_marks:
            return eng_marks[lower_eng_marks.index(response.lower())]
        else:
            return None
