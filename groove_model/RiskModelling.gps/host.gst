<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">
    <graph role="graph" edgeids="false" edgemode="directed" id="host">
        <attr name="$version">
            <string>curly</string>
        </attr>
        <node id="n1">
            <attr name="layout">
                <string>576 131 19 19</string>
            </attr>
        </node>
        <node id="n0">
            <attr name="layout">
                <string>1119 13 19 19</string>
            </attr>
        </node>
        <node id="n24">
            <attr name="layout">
                <string>354 487 19 19</string>
            </attr>
        </node>
        <node id="n9">
            <attr name="layout">
                <string>70 455 19 19</string>
            </attr>
        </node>
        <node id="n5">
            <attr name="layout">
                <string>264 262 19 19</string>
            </attr>
        </node>
        <node id="n2">
            <attr name="layout">
                <string>830 234 19 19</string>
            </attr>
        </node>
        <node id="n6">
            <attr name="layout">
                <string>740 363 19 19</string>
            </attr>
        </node>
        <node id="n10">
            <attr name="layout">
                <string>551 507 19 19</string>
            </attr>
        </node>
        <node id="n11">
            <attr name="layout">
                <string>1067 329 19 19</string>
            </attr>
        </node>
        <node id="n19">
            <attr name="layout">
                <string>1485 505 19 19</string>
            </attr>
        </node>
        <node id="n21">
            <attr name="layout">
                <string>1570 662 19 19</string>
            </attr>
        </node>
        <node id="n17">
            <attr name="layout">
                <string>1794 720 19 19</string>
            </attr>
        </node>
        <node id="n7">
            <attr name="layout">
                <string>1309 228 19 19</string>
            </attr>
        </node>
        <node id="n3">
            <attr name="layout">
                <string>1288 127 19 19</string>
            </attr>
        </node>
        <node id="n26">
            <attr name="layout">
                <string>1576 274 19 19</string>
            </attr>
        </node>
        <node id="n4">
            <attr name="layout">
                <string>1777 190 19 19</string>
            </attr>
        </node>
        <node id="n8">
            <attr name="layout">
                <string>1926 330 19 19</string>
            </attr>
        </node>
        <node id="n16">
            <attr name="layout">
                <string>2032 446 19 19</string>
            </attr>
        </node>
        <node id="n12">
            <attr name="layout">
                <string>1822 459 19 19</string>
            </attr>
        </node>
        <node id="n13">
            <attr name="layout">
                <string>150 567 19 19</string>
            </attr>
        </node>
        <node id="n14">
            <attr name="layout">
                <string>671 609 19 19</string>
            </attr>
        </node>
        <node id="n22">
            <attr name="layout">
                <string>681 768 19 19</string>
            </attr>
        </node>
        <node id="n25">
            <attr name="layout">
                <string>984 557 19 19</string>
            </attr>
        </node>
        <node id="n15">
            <attr name="layout">
                <string>1227 432 19 19</string>
            </attr>
        </node>
        <node id="n20">
            <attr name="layout">
                <string>1400 699 19 19</string>
            </attr>
        </node>
        <node id="n18">
            <attr name="layout">
                <string>1401 857 19 19</string>
            </attr>
        </node>
        <node id="n23">
            <attr name="layout">
                <string>1128 590 130 80</string>
            </attr>
        </node>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>type:Department</string>
            </attr>
        </edge>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>let:name="Sales"</string>
            </attr>
        </edge>
        <edge from="n1" to="n5">
            <attr name="label">
                <string>employs</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>type:Organization</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>let:name="ABC Software Inc."</string>
            </attr>
        </edge>
        <edge from="n0" to="n3">
            <attr name="label">
                <string>has_department</string>
            </attr>
        </edge>
        <edge from="n0" to="n4">
            <attr name="label">
                <string>has_department</string>
            </attr>
            <attr name="layout">
                <string>500 0 1247 25 1477 123 1706 237 11</string>
            </attr>
        </edge>
        <edge from="n0" to="n1">
            <attr name="label">
                <string>has_department</string>
            </attr>
            <attr name="layout">
                <string>500 0 1037 38 922 59 638 128 11</string>
            </attr>
        </edge>
        <edge from="n0" to="n2">
            <attr name="label">
                <string>has_department</string>
            </attr>
            <attr name="layout">
                <string>274 0 1077 42 1077 123 866 228 11</string>
            </attr>
        </edge>
        <edge from="n24" to="n24">
            <attr name="label">
                <string>type:Credentials</string>
            </attr>
        </edge>
        <edge from="n24" to="n24">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n24" to="n24">
            <attr name="label">
                <string>let:owner="EMP001"</string>
            </attr>
        </edge>
        <edge from="n24" to="n24">
            <attr name="label">
                <string>let:reused=false</string>
            </attr>
        </edge>
        <edge from="n9" to="n9">
            <attr name="label">
                <string>type:Device</string>
            </attr>
        </edge>
        <edge from="n9" to="n9">
            <attr name="label">
                <string>let:accepts_ntlm=true</string>
            </attr>
        </edge>
        <edge from="n9" to="n9">
            <attr name="label">
                <string>let:deviceType="laptop"</string>
            </attr>
        </edge>
        <edge from="n9" to="n9">
            <attr name="label">
                <string>let:os="Windows 10"</string>
            </attr>
        </edge>
        <edge from="n5" to="n5">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n5" to="n5">
            <attr name="label">
                <string>let:name="Alice"</string>
            </attr>
        </edge>
        <edge from="n5" to="n13">
            <attr name="label">
                <string>owns</string>
            </attr>
        </edge>
        <edge from="n5" to="n24">
            <attr name="label">
                <string>has_credentials</string>
            </attr>
        </edge>
        <edge from="n5" to="n9">
            <attr name="label">
                <string>uses</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>type:Department</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>let:name="Engineering"</string>
            </attr>
        </edge>
        <edge from="n2" to="n6">
            <attr name="label">
                <string>employs</string>
            </attr>
        </edge>
        <edge from="n6" to="n6">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n6" to="n6">
            <attr name="label">
                <string>let:name="Bob"</string>
            </attr>
        </edge>
        <edge from="n6" to="n10">
            <attr name="label">
                <string>uses</string>
            </attr>
        </edge>
        <edge from="n6" to="n25">
            <attr name="label">
                <string>has_credentials</string>
            </attr>
        </edge>
        <edge from="n6" to="n14">
            <attr name="label">
                <string>owns</string>
            </attr>
        </edge>
        <edge from="n10" to="n10">
            <attr name="label">
                <string>type:Device</string>
            </attr>
        </edge>
        <edge from="n10" to="n10">
            <attr name="label">
                <string>let:accepts_ntlm=false</string>
            </attr>
        </edge>
        <edge from="n10" to="n10">
            <attr name="label">
                <string>let:deviceType="laptop"</string>
            </attr>
        </edge>
        <edge from="n10" to="n10">
            <attr name="label">
                <string>let:os="Ubuntu"</string>
            </attr>
        </edge>
        <edge from="n11" to="n11">
            <attr name="label">
                <string>type:Device</string>
            </attr>
        </edge>
        <edge from="n11" to="n11">
            <attr name="label">
                <string>let:accepts_ntlm=false</string>
            </attr>
        </edge>
        <edge from="n11" to="n11">
            <attr name="label">
                <string>let:deviceType="desktop"</string>
            </attr>
        </edge>
        <edge from="n11" to="n11">
            <attr name="label">
                <string>let:os="Windows 10"</string>
            </attr>
        </edge>
        <edge from="n19" to="n19">
            <attr name="label">
                <string>type:Host</string>
            </attr>
        </edge>
        <edge from="n19" to="n19">
            <attr name="label">
                <string>let:accepts_ntlm=true</string>
            </attr>
        </edge>
        <edge from="n19" to="n19">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n19" to="n19">
            <attr name="label">
                <string>let:os="Windows"</string>
            </attr>
        </edge>
        <edge from="n19" to="n21">
            <attr name="label">
                <string>runs</string>
            </attr>
        </edge>
        <edge from="n19" to="n20">
            <attr name="label">
                <string>can_access</string>
            </attr>
        </edge>
        <edge from="n21" to="n21">
            <attr name="label">
                <string>type:Service</string>
            </attr>
        </edge>
        <edge from="n21" to="n21">
            <attr name="label">
                <string>let:exposed=true</string>
            </attr>
        </edge>
        <edge from="n21" to="n21">
            <attr name="label">
                <string>let:type="RDP"</string>
            </attr>
        </edge>
        <edge from="n17" to="n17">
            <attr name="label">
                <string>type:Server</string>
            </attr>
        </edge>
        <edge from="n17" to="n17">
            <attr name="label">
                <string>let:accepts_ntlm=true</string>
            </attr>
        </edge>
        <edge from="n17" to="n17">
            <attr name="label">
                <string>let:name="RDP-Server"</string>
            </attr>
        </edge>
        <edge from="n17" to="n17">
            <attr name="label">
                <string>let:os="Windows Server 2019"</string>
            </attr>
        </edge>
        <edge from="n17" to="n19">
            <attr name="label">
                <string>runs_on</string>
            </attr>
        </edge>
        <edge from="n7" to="n7">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n7" to="n7">
            <attr name="label">
                <string>let:name="Charlie"</string>
            </attr>
        </edge>
        <edge from="n7" to="n19">
            <attr name="label">
                <string>credentials_stored_on</string>
            </attr>
        </edge>
        <edge from="n7" to="n15">
            <attr name="label">
                <string>owns</string>
            </attr>
        </edge>
        <edge from="n7" to="n11">
            <attr name="label">
                <string>uses</string>
            </attr>
        </edge>
        <edge from="n7" to="n26">
            <attr name="label">
                <string>has_hash</string>
            </attr>
        </edge>
        <edge from="n3" to="n3">
            <attr name="label">
                <string>type:Department</string>
            </attr>
        </edge>
        <edge from="n3" to="n3">
            <attr name="label">
                <string>let:name="IT"</string>
            </attr>
        </edge>
        <edge from="n3" to="n7">
            <attr name="label">
                <string>employs</string>
            </attr>
        </edge>
        <edge from="n26" to="n26">
            <attr name="label">
                <string>type:CredentialHash</string>
            </attr>
        </edge>
        <edge from="n26" to="n26">
            <attr name="label">
                <string>let:owner="EMP003"</string>
            </attr>
        </edge>
        <edge from="n26" to="n26">
            <attr name="label">
                <string>let:stolen=false</string>
            </attr>
        </edge>
        <edge from="n4" to="n4">
            <attr name="label">
                <string>type:Department</string>
            </attr>
        </edge>
        <edge from="n4" to="n4">
            <attr name="label">
                <string>let:name="HR"</string>
            </attr>
        </edge>
        <edge from="n4" to="n8">
            <attr name="label">
                <string>employs</string>
            </attr>
        </edge>
        <edge from="n8" to="n8">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n8" to="n8">
            <attr name="label">
                <string>let:name="Diana"</string>
            </attr>
        </edge>
        <edge from="n8" to="n16">
            <attr name="label">
                <string>owns</string>
            </attr>
        </edge>
        <edge from="n8" to="n12">
            <attr name="label">
                <string>uses</string>
            </attr>
        </edge>
        <edge from="n16" to="n16">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n16" to="n16">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n16" to="n16">
            <attr name="label">
                <string>let:domain="example.com"</string>
            </attr>
        </edge>
        <edge from="n16" to="n16">
            <attr name="label">
                <string>let:role="user"</string>
            </attr>
        </edge>
        <edge from="n16" to="n16">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
        <edge from="n12" to="n12">
            <attr name="label">
                <string>type:Device</string>
            </attr>
        </edge>
        <edge from="n12" to="n12">
            <attr name="label">
                <string>let:accepts_ntlm=false</string>
            </attr>
        </edge>
        <edge from="n12" to="n12">
            <attr name="label">
                <string>let:deviceType="desktop"</string>
            </attr>
        </edge>
        <edge from="n12" to="n12">
            <attr name="label">
                <string>let:os="Windows 10"</string>
            </attr>
        </edge>
        <edge from="n13" to="n13">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n13" to="n13">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n13" to="n13">
            <attr name="label">
                <string>let:domain="example.com"</string>
            </attr>
        </edge>
        <edge from="n13" to="n13">
            <attr name="label">
                <string>let:role="user"</string>
            </attr>
        </edge>
        <edge from="n13" to="n13">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
        <edge from="n14" to="n14">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n14" to="n14">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n14" to="n14">
            <attr name="label">
                <string>let:domain="example.com"</string>
            </attr>
        </edge>
        <edge from="n14" to="n14">
            <attr name="label">
                <string>let:role="user"</string>
            </attr>
        </edge>
        <edge from="n14" to="n14">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
        <edge from="n14" to="n22">
            <attr name="label">
                <string>can_write</string>
            </attr>
        </edge>
        <edge from="n22" to="n22">
            <attr name="label">
                <string>type:File</string>
            </attr>
        </edge>
        <edge from="n22" to="n22">
            <attr name="label">
                <string>let:isSensitive=true</string>
            </attr>
        </edge>
        <edge from="n22" to="n22">
            <attr name="label">
                <string>let:name="config.sh"</string>
            </attr>
        </edge>
        <edge from="n22" to="n22">
            <attr name="label">
                <string>let:tampered=false</string>
            </attr>
        </edge>
        <edge from="n25" to="n25">
            <attr name="label">
                <string>type:Credentials</string>
            </attr>
        </edge>
        <edge from="n25" to="n25">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n25" to="n25">
            <attr name="label">
                <string>let:owner="EMP002"</string>
            </attr>
        </edge>
        <edge from="n25" to="n25">
            <attr name="label">
                <string>let:reused=true</string>
            </attr>
        </edge>
        <edge from="n15" to="n15">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n15" to="n15">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n15" to="n15">
            <attr name="label">
                <string>let:domain="example.com"</string>
            </attr>
        </edge>
        <edge from="n15" to="n15">
            <attr name="label">
                <string>let:role="admin"</string>
            </attr>
        </edge>
        <edge from="n15" to="n15">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
        <edge from="n15" to="n23">
            <attr name="label">
                <string>can_read</string>
            </attr>
        </edge>
        <edge from="n20" to="n20">
            <attr name="label">
                <string>type:Host</string>
            </attr>
        </edge>
        <edge from="n20" to="n20">
            <attr name="label">
                <string>let:accepts_ntlm=false</string>
            </attr>
        </edge>
        <edge from="n20" to="n20">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n20" to="n20">
            <attr name="label">
                <string>let:os="Ubuntu"</string>
            </attr>
        </edge>
        <edge from="n18" to="n18">
            <attr name="label">
                <string>type:Server</string>
            </attr>
        </edge>
        <edge from="n18" to="n18">
            <attr name="label">
                <string>let:accepts_ntlm=false</string>
            </attr>
        </edge>
        <edge from="n18" to="n18">
            <attr name="label">
                <string>let:name="DB-Server"</string>
            </attr>
        </edge>
        <edge from="n18" to="n18">
            <attr name="label">
                <string>let:os="Ubuntu 20.04"</string>
            </attr>
        </edge>
        <edge from="n18" to="n20">
            <attr name="label">
                <string>runs_on</string>
            </attr>
        </edge>
        <edge from="n23" to="n23">
            <attr name="label">
                <string>type:File</string>
            </attr>
        </edge>
        <edge from="n23" to="n23">
            <attr name="label">
                <string>let:isSensitive=true</string>
            </attr>
        </edge>
        <edge from="n23" to="n23">
            <attr name="label">
                <string>let:name="accounts.txt"</string>
            </attr>
        </edge>
        <edge from="n23" to="n23">
            <attr name="label">
                <string>let:tampered=false</string>
            </attr>
        </edge>
        <edge from="n23" to="n23">
            <attr name="label">
                <string>let:writable=false</string>
            </attr>
        </edge>
    </graph>
</gxl>
