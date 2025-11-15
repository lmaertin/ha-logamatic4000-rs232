# Dictionarys für die Zuordnung von IDs, Offsets and Topics
ID_OFFSET_MAPPING = {
    b"\xab\x00\x80": {
        0: {
            2: 'hk1_vorlauf_soll', 
            3: 'hk1_vorlauf_ist'
        }
    },
    b"\xab\x00\x81": {
        0: {
            2: 'hk2_vorlauf_soll', 
            3: 'hk2_vorlauf_ist'
        }
    },
    b"\xab\x00\x82": {
        0: {
            2: 'hk3_vorlauf_soll', 
            3: 'hk3_vorlauf_ist'
        }
    },
    b"\xab\x00\x83": {
        0: {
            2: 'hk4_vorlauf_soll', 
            3: 'hk4_vorlauf_ist'
        }
    },
    b"\xab\x00\x84": {
        0: {
            2: 'warmwasser_soll', 
            3: 'warmwasser_ist'
        }
    },
    b"\xab\x00\x88": {
        0: {
            0: 'kessel_vorlauf_soll', 
            1: 'kessel_vorlauf_ist'
        },
        6: {
            0: 'kessel_fehler_string',
            1: 'kessel_betrieb_string',
            2: 'brenner_ansteuerung_string'
        },
        24: {
            3: 'kessel_ruecklauf_soll', 
            4: 'kessel_ruecklauf_ist'
        },
        30: {
            4: 'brenner_status_string'
        }
    },
    b"\xab\x00\x89": {
        0: {
            0: 'aussentemperatur_normal', 
            1: 'aussentemperatur_gedaempft'
        }
    }
}