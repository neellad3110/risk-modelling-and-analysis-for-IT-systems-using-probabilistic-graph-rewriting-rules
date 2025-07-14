<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">
    <graph role="graph" edgeids="false" edgemode="directed" id="phishing_start">
        <attr name="$version">
            <string>curly</string>
        </attr>
        <node id="n1">
            <attr name="layout">
                <string>402 359 19 19</string>
            </attr>
        </node>
        <node id="n0">
            <attr name="layout">
                <string>348 223 130 48</string>
            </attr>
        </node>
        <edge from="n1" to="n1">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n1" to="n0">
            <attr name="label">
                <string>owns</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>let:compromised=false</string>
            </attr>
        </edge>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
    </graph>
</gxl>
