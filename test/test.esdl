<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" version="1" id="37e0284d-29f8-453e-91ec-2e7e02b5c16d" name="EnergySystem" description="Small energy system with assets used in GO-e" esdlVersion="v2211">
  <energySystemInformation xsi:type="esdl:EnergySystemInformation" id="8c79e632-1d89-4198-b055-157856e6fc9f">
    <carriers xsi:type="esdl:Carriers" id="02fafa20-a1bd-488e-a4db-f3c0ca7ff51a">
      <carrier xsi:type="esdl:ElectricityCommodity" id="d88696c0-b536-466b-adbf-429f282afeab" name="Electricity"/>
    </carriers>
  </energySystemInformation>
  <instance xsi:type="esdl:Instance" id="7972c9af-a7c9-4b06-9538-070cfa25291b" name="instance">
    <area xsi:type="esdl:Area" id="757e25b5-908f-4934-a16d-880c63c84406" name="area_title">
      <asset xsi:type="esdl:Bus" name="bus" id="44530afd-832b-4acf-998d-5654359ed813" voltage="400.0">
        <geometry xsi:type="esdl:Point" lat="51.444378637449404" lon="5.326824188232422"/>
        <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="a663919d-43e7-4cd5-8e04-01ed1fd8f7d5" id="072ad846-fa1f-43f5-a67d-a16df3f88d21"/>
      </asset>
      <asset xsi:type="esdl:Building" name="house1" id="00ab1742-0480-4a1d-a668-d09f5bca9e2f">
        <geometry xsi:type="esdl:Point" lat="51.44436826693578" lon="5.327478647232056"/>
        <asset xsi:type="esdl:EConnection" name="connection1" id="f006d594-0743-4de5-a589-a6c2350898da">
          <geometry xsi:type="esdl:Point" lat="260.0" lon="52.0" CRS="Simple"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="072ad846-fa1f-43f5-a67d-a16df3f88d21" id="a663919d-43e7-4cd5-8e04-01ed1fd8f7d5"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="296f937e-2e89-4be9-9d70-86f98a3de9ec" id="711a37c7-604c-4906-8e61-cec2b2c8e3bb"/>
          <port xsi:type="esdl:InPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="85b715d0-9851-40a4-a432-969245779b2f" id="33d0e20e-f618-4133-8eab-aa1bbb57e2ea"/>
        </asset>
        <asset xsi:type="esdl:PVInstallation" power="1000.0" name="pv-installation1" id="176af591-6d9d-4751-bb0f-fac7e99b1c3d" panelEfficiency="0.2">
          <geometry xsi:type="esdl:Point" lat="415.0" lon="236.0" CRS="Simple"/>
          <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="711a37c7-604c-4906-8e61-cec2b2c8e3bb" id="296f937e-2e89-4be9-9d70-86f98a3de9ec"/>
        </asset>
        <asset xsi:type="esdl:PVInstallation" power="1000.0" name="pv-installation1" id="b8766109-5328-416f-9991-e81a5cada8a6" panelEfficiency="0.2">
          <geometry xsi:type="esdl:Point" lat="365.0" lon="236.0" CRS="Simple"/>
          <port xsi:type="esdl:OutPort" carrier="d88696c0-b536-466b-adbf-429f282afeab" connectedTo="33d0e20e-f618-4133-8eab-aa1bbb57e2ea" id="85b715d0-9851-40a4-a432-969245779b2f"/>
        </asset>
      </asset>
      <asset xsi:type="esdl:Building" originalIdInSource="8551" id="b4ab231f-883c-41f7-a4a8-606646cca82d" name="House2" >
        <asset xsi:type="esdl:EConnection" originalIdInSource="8551" id="fd7fc047-30b1-48e3-99d9-1bc882772170" name="connection2" >
          <port xsi:type="esdl:InPort" id="f0552095-9270-4983-8929-a8e5d6edaf5a" connectedTo="072ad846-fa1f-43f5-a67d-a16df3f88d21" name="In"/>
          <port xsi:type="esdl:OutPort" id="f3663d2c-b657-450f-99ef-33b83380e3f5" connectedTo="dacf2176-3534-479f-9398-54193e4de76e" name="OutPh1"/>
          <port xsi:type="esdl:OutPort" id="bc7944b6-318c-449b-81e6-2826d3c40e8b" connectedTo="36a742e1-bdeb-44d8-8ece-3921241c393f" name="OutPh2"/>
          <port xsi:type="esdl:OutPort" id="746008be-3e07-46f7-bd2a-5588bce8e19c" connectedTo="b3e5c41a-82d8-4882-85ac-9ff5db5458c0" name="OutPh3"/>
          <geometry xsi:type="esdl:Point" lat="260.0" CRS="Simple" lon="52.0"/>
        </asset>
        <asset xsi:type="esdl:ElectricityNetwork" originalIdInSource="8551" id="3e92541b-0ec7-4240-b8ed-3f8f5ffc9f3c" name="PhasegridHome855_1_Ph1">
          <port xsi:type="esdl:InPort" id="dacf2176-3534-479f-9398-54193e4de76e" connectedTo="f3663d2c-b657-450f-99ef-33b83380e3f5" name="In"/>
          <port xsi:type="esdl:InPort" id="1026f5d8-b09b-4342-be67-e26a3b5a65ba" connectedTo="23708e7b-7870-46f6-ac58-9cafba1939b6"/>
          <geometry xsi:type="esdl:Point" lat="360.0" CRS="Simple" lon="236.0"/>
        </asset>
        <asset xsi:type="esdl:ElectricityNetwork" originalIdInSource="8551" id="f31e99da-99e4-4b86-9a53-2daedb10554b" name="PhasegridHome855_1_Ph2">
          <port xsi:type="esdl:InPort" id="36a742e1-bdeb-44d8-8ece-3921241c393f" connectedTo="bc7944b6-318c-449b-81e6-2826d3c40e8b" name="In"/>
          <port xsi:type="esdl:InPort" id="a33b253f-6ac5-4494-ba6c-fd93da535ccb" connectedTo="721856ed-5e9b-4fd3-b3ae-cce13c8f3436"/>
          <port xsi:type="esdl:OutPort" id="b46fc288-3f1d-4f3c-bab6-532ba803af3a" connectedTo="7a3affa2-1d0c-4817-9005-1cbdf9802e9a"/>
          <geometry xsi:type="esdl:Point" lat="260.0" CRS="Simple" lon="236.0"/>
        </asset>
        <asset xsi:type="esdl:ElectricityNetwork" originalIdInSource="8551" id="bfe2158c-84bb-4583-a193-536d2974811b" name="PhasegridHome855_1_Ph3">
          <port xsi:type="esdl:InPort" id="b3e5c41a-82d8-4882-85ac-9ff5db5458c0" connectedTo="746008be-3e07-46f7-bd2a-5588bce8e19c" name="In"/>
          <port xsi:type="esdl:InPort" id="d17fd77e-4852-49e6-b085-53f259cf2836" connectedTo="66288ac7-c94a-4803-b9b7-a9e4731cee0a"/>
          <geometry xsi:type="esdl:Point" lat="160.0" CRS="Simple" lon="236.0"/>
        </asset>
        <asset xsi:type="esdl:PVInstallation" id="a9e47c95-e0ad-45fd-88e4-fe7c982ac677" powerFactor="1.0" name="pv_Home855_1" surfaceArea="42" panelEfficiency="0.2">
          <port xsi:type="esdl:OutPort" id="23708e7b-7870-46f6-ac58-9cafba1939b6" connectedTo="1026f5d8-b09b-4342-be67-e26a3b5a65ba"/>
          <port xsi:type="esdl:OutPort" id="721856ed-5e9b-4fd3-b3ae-cce13c8f3436" connectedTo="a33b253f-6ac5-4494-ba6c-fd93da535ccb"/>
          <port xsi:type="esdl:OutPort" id="66288ac7-c94a-4803-b9b7-a9e4731cee0a" connectedTo="d17fd77e-4852-49e6-b085-53f259cf2836"/>
          <geometry xsi:type="esdl:Point" lat="415.0" CRS="Simple" lon="236.0"/>
        </asset>
        <asset xsi:type="esdl:HeatPump" id="ad7df8a2-6a34-4b5a-8b23-f077963507ec" COP="3.5" power="14500.0" name="hp_Home855_1" description="{&quot;buffer_capacitance&quot;: 1213070.0, &quot;buffer_temp_set&quot;: 313.15, &quot;buffer_temp_min&quot;: 298.15, &quot;buffer_temp_max&quot;: 338.15, &quot;buffer_temp_0&quot;: 315.93853596915767, &quot;buffer_temp_hor&quot;: 313.15, &quot;dhw_capacitance&quot;: 836600.0, &quot;dhw_temp_set&quot;: 328.15, &quot;dhw_temp_min&quot;: 298.15, &quot;dhw_temp_max&quot;: 358.15, &quot;dhw_temp_0&quot;: 318.6502151044533, &quot;dhw_temp_hor&quot;: 328.15, &quot;dhw_temp_tap&quot;: 288.15, &quot;heat_element&quot;: 3000.0, &quot;cop_element&quot;: 1.0, &quot;house_temp_set&quot;: 292.65, &quot;house_temp_min&quot;: 291.84999999999997, &quot;house_temp_max&quot;: 293.45, &quot;house_temp_0&quot;: 292.4459134830428, &quot;house_temp_hor&quot;: 292.65}" assetType="vrijst+1992-2005+family" powerFactor="0.95">
          <port xsi:type="esdl:InPort" id="7a3affa2-1d0c-4817-9005-1cbdf9802e9a" connectedTo="b46fc288-3f1d-4f3c-bab6-532ba803af3a">
            <profile xsi:type="esdl:TimeSeriesProfile" startDateTime="2020-01-14T00:00:00.000000" values="0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0269180517184188 0.0 0.0 0.0 0.0012905349794238 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0152157214137332 0.0813037037037038 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0038716049382716 0.0 0.0 0.0 0.0211833333333332 0.0471499999999998 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0006262806064462 0.0 0.0 0.0 0.0098941015089163 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.021171638408021 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0182222222222222 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0391511659807952 0.0234351165980795 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0033135982955822 0.0 0.0 0.0094639231824416 0.0021508916323731 0.0 0.0 0.0 0.0086035665294924 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0" timestep="288"/>
          </port>
        </asset>
        <geometry xsi:type="esdl:Point" lat="8352.28010349294" CRS="WGS84" lon="-16227.342701724223"/>
      </asset>
    </area>
  </instance>
  <services xsi:type="esdl:Services" id="7000c29e-8f08-4bd1-b420-5904767e297f">
    <service xsi:type="esdl:EnergyMarket" id="b612fc89-a752-4a30-84bb-81ebffc56b50" name="DA-market">
      <marketPrice xsi:type="esdl:DateTimeProfile">
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:15:00.000000" from="2020-01-14T00:00:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:30:00.000000" from="2020-01-14T00:15:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T00:45:00.000000" from="2020-01-14T00:30:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:00:00.000000" from="2020-01-14T00:45:00.000000" value="0.135"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:15:00.000000" from="2020-01-14T01:00:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:30:00.000000" from="2020-01-14T01:15:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T01:45:00.000000" from="2020-01-14T01:30:00.000000" value="0.1172"/>
        <element xsi:type="esdl:ProfileElement" to="2020-01-14T02:00:00.000000" from="2020-01-14T01:45:00.000000" value="0.1172"/>
      </marketPrice>
    </service>
  </services>
</esdl:EnergySystem>
