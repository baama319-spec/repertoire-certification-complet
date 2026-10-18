<template>
	<div class="table"><table>
		<thead><tr><th>Client　⌃</th><th>Téléphone　⌃</th><th>Adresse principale　⌃</th><th>Demandes effectuées　⌃</th><th>Statut compte　⌃</th><th>Actions</th></tr></thead>
		<tbody><tr v-for="client in clients" :key="client.id">
			<td class="person"><img :src="client.image" :alt="client.name"><span><b>{{client.name}}</b></span></td>
			<td class="contact"><span>{{client.phone}}</span></td>
			<td>{{client.address}}</td>
			<td>{{client.requests}} demande{{client.requests > 1 ? 's' : ''}}</td>
			<td><mark :class="client.status === 'Actif' ? 'active' : 'blocked'">{{client.status}}</mark></td>
			<td class="actions"><button @click="$emit('view', client)">Voir</button><button :class="client.status === 'Bloqué' ? 'unlock' : ''" @click="$emit('toggle', client)">{{client.status === 'Bloqué' ? 'Débloquer' : 'Bloquer'}}</button></td>
		</tr></tbody>
	</table></div>
</template>
<script setup>defineProps({clients:{type:Array,default:()=>[]}});defineEmits(['view','toggle'])</script>
<style scoped>.table{overflow:auto;border:1px solid #d9eafb;border-radius:10px}table{width:100%;min-width:0;border-collapse:collapse;table-layout:fixed}th{text-align:left;height:58px;padding:14px 17px;background:#eef7ff;text-transform:uppercase;color:#1764dc;font-size:11px}th:nth-child(1){width:18%}th:nth-child(2){width:19%}th:nth-child(3){width:16%}th:nth-child(4){width:17%}th:nth-child(5){width:14%}th:nth-child(6){width:16%}td{height:108px;padding:14px 17px;border-bottom:1px solid #dcecfb;color:#2160c3;font-size:13px}.person{display:flex;align-items:center;gap:16px;color:#15535a}.person img{width:62px;height:62px;border-radius:50%;object-fit:cover}.person b,.person small,.contact span{display:block}.person b{font-size:14px}.person small{width:max-content;margin-top:8px;padding:4px 9px;border-radius:13px;background:#e7f2ff;color:#4a7fd0;font-size:10px}.contact{line-height:2.45}.contact span:last-child{font-size:12px}mark{display:inline-block;border:0;border-radius:18px;padding:10px 17px;font-size:12px}.active{background:#dff9ed;color:#00a66a}.blocked{background:#ffe7ec;color:#f33650}.actions{white-space:nowrap}.actions button{min-width:94px;padding:10px 12px;border:1px solid #68a4ff;border-radius:7px;background:#fff;color:#087f70;font-size:12px}.actions button+button{margin-left:8px;border-color:#ff8092;color:#f33550}.actions .unlock{border-color:#54d8a5;color:#00a66a}</style>
