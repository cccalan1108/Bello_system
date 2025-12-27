<template>
  <div v-if="show" class="map-modal-overlay" @click.self="closeModal">
    <div class="map-modal-dialog">
      <div class="map-modal-content">
        <div class="map-modal-header">
          <h5 class="map-modal-title">📍 {{ placeName }}</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="map-modal-body">
          <!-- 載入中 -->
          <div v-if="loading" class="map-loading">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">載入中...</span>
            </div>
            <p class="mt-2 mb-0">載入地圖中...</p>
          </div>
          <!-- 錯誤狀態 -->
          <div v-else-if="mapError" class="map-error">
            <p>⚠️ 無法載入地圖</p>
            <p class="text-muted small">請點擊下方按鈕在 Google Maps 中查看</p>
          </div>
          <!-- 地圖容器 -->
          <div v-show="!loading && !mapError" ref="mapContainer" class="map-container"></div>
          <div v-if="address" class="address-info">
            <strong>地址：</strong>{{ address }}
          </div>
        </div>
        <div class="map-modal-footer">
          <a 
            :href="googleMapsUrl" 
            target="_blank" 
            class="btn btn-primary"
          >
            在 Google Maps 開啟
          </a>
          <button type="button" class="btn btn-secondary" @click="closeModal">關閉</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { loadGoogleMapsAPI } from '@/utils/googleMaps'

export default {
  name: 'MapModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    placeName: {
      type: String,
      default: ''
    },
    address: {
      type: String,
      default: ''
    },
    latitude: {
      type: Number,
      default: null
    },
    longitude: {
      type: Number,
      default: null
    }
  },
  emits: ['close'],
  data() {
    return {
      map: null,
      marker: null,
      mapError: false,
      loading: false
    }
  },
  computed: {
    googleMapsUrl() {
      if (this.latitude && this.longitude) {
        return `https://www.google.com/maps/search/?api=1&query=${this.latitude},${this.longitude}`
      }
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(this.placeName + ' ' + this.address)}`
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.loadAndInitMap()
        })
      }
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
    },
    async loadAndInitMap() {
      if (!this.latitude || !this.longitude) {
        console.warn('No coordinates provided for map')
        this.mapError = true
        return
      }

      this.loading = true
      this.mapError = false

      try {
        await loadGoogleMapsAPI()
        this.initMap()
      } catch (error) {
        console.error('Google Maps API 載入失敗:', error)
        this.mapError = true
      } finally {
        this.loading = false
      }
    },
    initMap() {
      if (typeof google === 'undefined' || !google.maps) {
        console.warn('Google Maps API not available')
        return
      }

      const position = { lat: this.latitude, lng: this.longitude }

      this.map = new google.maps.Map(this.$refs.mapContainer, {
        center: position,
        zoom: 16,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
      })

      this.marker = new google.maps.Marker({
        position: position,
        map: this.map,
        title: this.placeName
      })
    }
  }
}
</script>

<style scoped>
.map-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.map-modal-dialog {
  max-width: 600px;
  width: 95%;
  max-height: 90vh;
}

.map-modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.map-modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-modal-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.map-modal-body {
  padding: 0;
}

.map-container {
  width: 100%;
  height: 300px;
}

.map-loading,
.map-error {
  width: 100%;
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  color: #6c757d;
}

.address-info {
  padding: 1rem 1.25rem;
  background-color: #f8f9fa;
  font-size: 0.9rem;
  color: #495057;
}

.map-modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>

