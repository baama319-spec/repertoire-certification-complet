<template>
  <div class="request-table">
    <table>
      <colgroup>
        <col class="idcol">
        <col class="datecol">
        <col class="clientcol">
        <col class="devicecol">
        <col class="statuscol">
        <col class="actioncol">
      </colgroup>
      <thead>
        <tr>
          <th>ID Demande</th>
          <th>Date</th>
          <th>Client</th>
          <th>Appareil</th>
          <th>Statut</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in demandes" :key="item.id">
          <td class="id" data-label="ID Demande">{{ item.id }}</td>
          <td class="date" data-label="Date">{{ item.date }}</td>
          <td class="client" data-label="Client">{{ item.client }}</td>
          <td class="device" data-label="Appareil">{{ item.device }}</td>
          <td data-label="Statut"><mark :class="item.status.toLowerCase().replace(' ', '-')">{{ item.status }}</mark></td>
          <td class="actions" data-label="Actions">
            <button type="button" class="detail" @click="$emit('detail', item)">Voir plus</button>
            <button type="button" class="delete" @click="$emit('delete', item)">Supprimer</button>
          </td>
        </tr>
        <tr v-if="!demandes.length">
          <td colspan="6" class="empty">Aucune demande ne correspond à la recherche.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({ demandes: { type: Array, required: true } })
defineEmits(['detail', 'delete'])
</script>

<style scoped>
.request-table{width:100%;margin:2px 0 0;overflow:hidden;border:1px solid #ddebfb;border-radius:9px;background:#fff;font-family:Inter,Arial,sans-serif}
table{width:100%;border-collapse:collapse;table-layout:fixed;background:#fff}
.idcol{width:7%}.datecol{width:14%}.clientcol{width:18%}.devicecol{width:21%}.statuscol{width:14%}.actioncol{width:26%}
th{height:58px;padding:12px 14px;text-align:left;text-transform:uppercase;color:#fff;background:#143653;font-size:12px;font-weight:700;letter-spacing:.02em}
td{height:90px;padding:13px 14px;border-bottom:1px solid #dfeefa;color:#496b9e;font-size:12px;font-weight:500;line-height:1.45;overflow-wrap:anywhere}
tbody tr:nth-child(even){background:#f0faf8}tbody tr:nth-child(odd){background:#fff}tbody tr:last-child td{border:0}
.id{font-size:13px;font-weight:800;color:#12376c}.date{color:#5576a7;font-size:12px}.client{font-size:13px;font-weight:700;color:#12376c}.device{font-size:13px;font-weight:700;color:#12376c}
.actions{display:flex;align-items:center;gap:8px;white-space:normal}
.actions button{min-width:0;flex:1;padding:10px 8px;border-radius:8px;background:#fff;font-size:11px;font-weight:700;white-space:nowrap}
.detail{border:1px solid #77aeff;color:#087f70}.delete{border:1px solid #ff879a;color:#f03650}
mark{display:inline-block;padding:8px 11px;border-radius:22px;background:#fff0d7;color:#a86700;font-size:11px;font-weight:600;white-space:nowrap}
mark.acceptée{background:#ddf8ed;color:#008b68}.empty{height:110px;text-align:center;color:#6681b2}
@media(max-width:900px){th,td{padding-left:9px;padding-right:9px;font-size:12px}.actioncol{width:28%}.actions{flex-direction:column;align-items:stretch;gap:5px}.actions button{width:100%;padding:7px 5px;font-size:11px}}
@media(max-width:620px){.request-table{overflow:visible;border:0;background:transparent}table,tbody{display:block;width:100%}thead{display:none}tbody tr{display:grid;grid-template-columns:1fr 1fr;margin-bottom:12px;overflow:hidden;border:1px solid #ddebfb;border-radius:10px;background:#fff!important;box-shadow:0 4px 14px #153b5910}td{display:flex;min-width:0;height:auto;min-height:48px;align-items:center;justify-content:space-between;gap:8px;padding:10px 12px;border-bottom:1px solid #edf3f8;font-size:12px}td::before{content:attr(data-label);flex:none;color:#71849b;font-size:10px;font-weight:700;text-transform:uppercase}.actions{grid-column:1/-1;flex-direction:row;justify-content:flex-end;border-bottom:0}.actions button{width:auto;flex:1;padding:9px 6px}.empty{grid-column:1/-1;height:auto;min-height:70px;justify-content:center}.empty::before{content:none}}
</style>