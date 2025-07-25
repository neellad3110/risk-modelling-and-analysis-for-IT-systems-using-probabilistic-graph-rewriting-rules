<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">
    <graph role="graph" edgeids="false" edgemode="directed" id="credentials_dumping_start">
        <attr name="$version">
            <string>curly</string>
        </attr>
        <node id="n0">
            <attr name="layout">
                <string>397 293 19 19</string>
            </attr>
        </node>
        <node id="n1">
            <attr name="layout">
                <string>354 430 111 54</string>
            </attr>
        </node>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>type:Host</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>let:compromised=true</string>
            </attr>
        </edge>
        <edge from="n1" to="n0">
            <attr name="label">
                <string>credentials_stored_on</string>
            </attr>
            <attr name="layout">
                <string>490 -5 409 469 406 302 11</string>
            </attr>
        </edge>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>let:role="admin"</string>
            </attr>
        </edge>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
    </graph>
</gxl>
