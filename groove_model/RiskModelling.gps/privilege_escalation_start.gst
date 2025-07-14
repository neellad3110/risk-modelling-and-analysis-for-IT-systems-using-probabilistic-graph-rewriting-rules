<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<gxl xmlns="http://www.gupro.de/GXL/gxl-1.0.dtd">
    <graph role="graph" edgeids="false" edgemode="directed" id="privilege_escalation_start">
        <attr name="$version">
            <string>curly</string>
        </attr>
        <node id="n0">
            <attr name="layout">
                <string>400 460 19 19</string>
            </attr>
        </node>
        <node id="n3">
            <attr name="layout">
                <string>150 290 19 19</string>
            </attr>
        </node>
        <node id="n2">
            <attr name="layout">
                <string>345 270 122 64</string>
            </attr>
        </node>
        <edge from="n0" to="n0">
            <attr name="label">
                <string>type:User</string>
            </attr>
        </edge>
        <edge from="n0" to="n2">
            <attr name="label">
                <string>owns</string>
            </attr>
            <attr name="layout">
                <string>490 -5 409 469 406 302 11</string>
            </attr>
        </edge>
        <edge from="n3" to="n3">
            <attr name="label">
                <string>type:File</string>
            </attr>
        </edge>
        <edge from="n3" to="n3">
            <attr name="label">
                <string>let:isSensitive=true</string>
            </attr>
        </edge>
        <edge from="n3" to="n3">
            <attr name="label">
                <string>let:tampered=false</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>type:EmailAccount</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>let:compromised=true</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>let:role="user"</string>
            </attr>
        </edge>
        <edge from="n2" to="n2">
            <attr name="label">
                <string>let:status="active"</string>
            </attr>
        </edge>
        <edge from="n2" to="n3">
            <attr name="label">
                <string>can_write</string>
            </attr>
        </edge>
    </graph>
</gxl>
