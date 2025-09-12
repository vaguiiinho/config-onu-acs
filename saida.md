✅ Conectado com sucesso!

[CMD] Executando: cd onu
[CMD] Executando: show authorization slot 4 p 3

📋 Saída completa do comando:

show authorization slot 4 p 3
-----  ONU Auth Table, Total ITEM = 1417 -----

A: Authorized  P: Preauthorized  R: System Reserved

-----  ONU Auth Table, SLOT = 4, PON = 3, ITEM = 18 -----
Slot Pon Onu OnuType        ST Lic OST PhyId        PhyPwd     LogicId                  LogicPwd     
---- --- --- -------------- -- --- --- ------------ ---------- ------------------------ ------------
4    3   1   HG6145E        A  1   up  FHTT9d7c9f80                                                  
4    3   2   5506-04-FA     A  1   up  FHTT95f13ae0                                                  
4    3   3   5506-04-FA     A  1   up  FHTT9885ba08                                                  
4    3   4   5506-02-B      A  1   up  FHTT2399f8f0                                                  
4    3   5   5506-04-FA     A  1   up  FHTT95f157a0                                                  
4    3   6   5506-02-B      A  1   up  FHTT10f11300                                                  
4    3   7   5506-02-B      A  1   up                                                
4    3   8   5506-02-B      A  1   up  F                                              
4    3   9   5506-04-FA     A  1   up  F                                              
4    3   10  HG6145E        A  1   up  F                                              
4    3   11  5506-04-F1     A  1   up  F                                              
4    3   12  5506-04-F1     A  1   up  F                                              
4    3   13  5506-01-A1     A  1   up  F                                              
4    3   14  HG6145E        A  1   up  F                                              
4    3   15  HG6145E        A  1   up  F                                              
4    3   16  HG6145E        A  1   up  F                                              
4    3   17  HG6145E        A  1   up  F                                              
4    3   18  5506-04-FA     A  1   up  F                                              
                                              
✅ Compatível: Slot 4, PON 3, ONU 1, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 2, Tipo 5506-04-FA
✅ Compatível: Slot 4, PON 3, ONU 3, Tipo 5506-04-FA
✅ Compatível: Slot 4, PON 3, ONU 5, Tipo 5506-04-FA
✅ Compatível: Slot 4, PON 3, ONU 9, Tipo 5506-04-FA
✅ Compatível: Slot 4, PON 3, ONU 10, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 14, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 15, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 16, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 17, Tipo HG6145E
✅ Compatível: Slot 4, PON 3, ONU 18, Tipo 5506-04-FA

📊 Total ONUs compatíveis: 11
[CMD] Executando: cd ..
[CMD] Executando: show startup-config module onu_wan

set wancfg sl 4 3 1 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis emr_aroeiras_fib@tubaron.net key:khl1k+3& null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 1 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 2 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis carlarubbo@tubaron.net key:&i5411m3 null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 2 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 3 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis h_luiz@tubaron.net key:20mke7fi null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 3 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 5 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro en joslainenoronha@tubaron.net key:f6&ii7*e null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 5 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 9 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis lisabetevieira@tubaron.net key:mjjj<)m& null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 9 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 10 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis leonardolopes@tubaron.net key:)jl*jf.g null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 10 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 14 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis regiscapaverde@tubaron.net key:6h$6=ee( null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 14 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 15 ind 1 mode tr069_in ty r 3800 0 nat en qos dis dsp pppoe pro dis carlgmm@tubaron.net key:,j(lj3:) null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5                                        
set wancfg sl 4 3 15 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 16 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis alexinterior@tubaron.net key:im3lgi6i null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 16 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 17 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis robertode@tubaron.com key:2h,%je7j null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 17 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
set wancfg sl 4 3 18 ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis alinedasilva@tubaron.net key:j;5l58-+ null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5
set wancfg sl 4 3 18 ind 1 ip-stack-mode ipv4 ipv6-src-type slaac prefix-src-type delegate
olt01.pbgce.tubaron.net.br-fh-sdfhiv439kvadj#

✅ Script finalizado!