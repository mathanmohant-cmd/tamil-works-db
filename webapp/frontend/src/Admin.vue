<template>
  <div class="admin-page">
    <h2>Collections Admin</h2>

    <div class="admin-layout">
      <!-- Left Panel: Collection Tree -->
      <div class="collections-panel">
        <div class="panel-header">
          <h3>Collections</h3>
          <button @click="showCreateForm" class="btn-primary">+ New Collection</button>
        </div>

        <div v-if="loading" class="loading">Loading collections...</div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else class="collection-tree">
          <CollectionNode
            v-for="collection in collectionTree"
            :key="collection.collection_id"
            :collection="collection"
            :selectedId="selectedCollection?.collection_id"
            @select="selectCollection"
          />
          <div v-if="collectionTree.length === 0" class="empty-state">
            No collections yet. Create one to get started.
          </div>
        </div>
      </div>

      <!-- Right Panel: Details/Form -->
      <div class="details-panel">
        <!-- Create/Edit Form -->
        <div v-if="showForm" class="collection-form">
          <h3>{{ editingCollection ? 'Edit Collection' : 'New Collection' }}</h3>

          <div class="form-group">
            <label>Name (English) *</label>
            <input v-model="formData.collection_name" type="text" required />
          </div>

          <div class="form-group">
            <label>Name (Tamil)</label>
            <input v-model="formData.collection_name_tamil" type="text" />
          </div>

          <div class="form-group">
            <label>Type *</label>
            <select v-model="formData.collection_type">
              <option value="period">Period</option>
              <option value="tradition">Tradition</option>
              <option value="genre">Genre</option>
              <option value="canon">Canon</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div class="form-group">
            <label>Parent Collection</label>
            <select v-model="formData.parent_collection_id">
              <option :value="null">-- None (Top Level) --</option>
              <option
                v-for="coll in flatCollections"
                :key="coll.collection_id"
                :value="coll.collection_id"
                :disabled="editingCollection && coll.collection_id === editingCollection.collection_id"
              >
                {{ coll.indent }}{{ coll.collection_name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Sort Order</label>
            <input v-model.number="formData.sort_order" type="number" />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="formData.description" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button @click="saveCollection" class="btn-primary" :disabled="!formData.collection_name">
              {{ editingCollection ? 'Update' : 'Create' }}
            </button>
            <button @click="cancelForm" class="btn-secondary">Cancel</button>
          </div>
        </div>

        <!-- Collection Details -->
        <div v-else-if="selectedCollection" class="collection-details">
          <div class="details-header">
            <h3>{{ selectedCollection.collection_name }}</h3>
            <div class="details-actions">
              <button @click="editCollection" class="btn-secondary">Edit</button>
              <button @click="confirmDelete" class="btn-danger">Delete</button>
            </div>
          </div>

          <div class="details-info">
            <p v-if="selectedCollection.collection_name_tamil">
              <strong>Tamil:</strong> {{ selectedCollection.collection_name_tamil }}
            </p>
            <p><strong>Type:</strong> {{ selectedCollection.collection_type }}</p>
            <p v-if="selectedCollection.parent_name">
              <strong>Parent:</strong> {{ selectedCollection.parent_name }}
            </p>
            <p v-if="selectedCollection.description">
              <strong>Description:</strong> {{ selectedCollection.description }}
            </p>
          </div>

          <!-- Works in Collection -->
          <div class="works-section">
            <div class="section-header">
              <h4>Works in this Collection ({{ selectedCollection.works?.length || 0 }})</h4>
              <button @click="showAddWork = true" class="btn-small">+ Add Work</button>
            </div>

            <div v-if="selectedCollection.works?.length > 0" class="works-list">
              <div
                v-for="work in selectedCollection.works"
                :key="work.work_id"
                class="work-item"
              >
                <div class="work-info">
                  <span class="work-position" v-if="work.position_in_collection">
                    #{{ work.position_in_collection }}
                  </span>
                  <span class="work-name">{{ work.work_name_tamil || work.work_name }}</span>
                  <span v-if="work.is_primary" class="primary-badge">Primary</span>
                </div>
                <button @click="removeWork(work.work_id)" class="btn-remove" title="Remove">×</button>
              </div>
            </div>
            <div v-else class="empty-works">
              No works assigned to this collection.
            </div>
          </div>

          <!-- Child Collections -->
          <div v-if="selectedCollection.children?.length > 0" class="children-section">
            <h4>Child Collections</h4>
            <ul>
              <li v-for="child in selectedCollection.children" :key="child.collection_id">
                <a href="#" @click.prevent="selectCollectionById(child.collection_id)">
                  {{ child.collection_name }}
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-details">
          <p>Select a collection to view details, or create a new one.</p>
        </div>
      </div>
    </div>

    <!-- Add Work Modal -->
    <div v-if="showAddWork" class="modal-overlay" @click="showAddWork = false">
      <div class="modal-content" @click.stop>
        <h3>Add Work to Collection</h3>

        <div class="form-group">
          <label>Select Work</label>
          <select v-model="addWorkData.work_id">
            <option :value="null">-- Select a work --</option>
            <option
              v-for="work in availableWorks"
              :key="work.work_id"
              :value="work.work_id"
            >
              {{ work.work_name_tamil }} ({{ work.work_name }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Position in Collection</label>
          <input v-model.number="addWorkData.position" type="number" min="1" />
        </div>

        <div class="form-group">
          <label>
            <input type="checkbox" v-model="addWorkData.is_primary" />
            Set as Primary Collection for this Work
          </label>
        </div>

        <div class="form-actions">
          <button @click="addWork" class="btn-primary" :disabled="!addWorkData.work_id">
            Add Work
          </button>
          <button @click="showAddWork = false" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="showDeleteConfirm = false">
      <div class="modal-content" @click.stop>
        <h3>Delete Collection?</h3>
        <p>Are you sure you want to delete "{{ selectedCollection?.collection_name }}"?</p>
        <p class="warning">This will remove all work associations. Child collections will become top-level.</p>
        <div class="form-actions">
          <button @click="deleteCollection" class="btn-danger">Delete</button>
          <button @click="showDeleteConfirm = false" class="btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from './api.js'

// Recursive CollectionNode component
const CollectionNode = {
  name: 'CollectionNode',
  props: {
    collection: Object,
    selectedId: Number,
    depth: { type: Number, default: 0 }
  },
  emits: ['select'],
  template: `
    <div class="tree-node" :style="{ paddingLeft: depth * 16 + 'px' }">
      <div
        class="tree-item"
        :class="{ selected: collection.collection_id === selectedId }"
        @click="$emit('select', collection)"
      >
        <span v-if="collection.children?.length" class="tree-icon">▶</span>
        <span v-else class="tree-icon">•</span>
        <span class="tree-name">{{ collection.collection_name }}</span>
        <span class="tree-count">({{ collection.work_count }})</span>
      </div>
      <div v-if="collection.children?.length" class="tree-children">
        <CollectionNode
          v-for="child in collection.children"
          :key="child.collection_id"
          :collection="child"
          :selectedId="selectedId"
          :depth="depth + 1"
          @select="$emit('select', $event)"
        />
      </div>
    </div>
  `
}

export default {
  name: 'Admin',
  components: { CollectionNode },
  setup() {
    const loading = ref(false)
    const error = ref(null)
    const collectionTree = ref([])
    const flatCollections = ref([])
    const selectedCollection = ref(null)
    const works = ref([])

    // Form state
    const showForm = ref(false)
    const editingCollection = ref(null)
    const formData = ref({
      collection_name: '',
      collection_name_tamil: '',
      collection_type: 'custom',
      description: '',
      parent_collection_id: null,
      sort_order: null
    })

    // Add work state
    const showAddWork = ref(false)
    const addWorkData = ref({
      work_id: null,
      position: null,
      is_primary: false
    })

    // Delete confirmation
    const showDeleteConfirm = ref(false)

    // Load collections
    const loadCollections = async () => {
      loading.value = true
      error.value = null
      try {
        const [treeRes, flatRes, worksRes] = await Promise.all([
          api.getCollectionTree(),
          api.getCollections({ include_works: false }),
          api.getWorks()
        ])
        collectionTree.value = treeRes.data
        works.value = worksRes.data

        // Build flat list with indentation for parent dropdown
        flatCollections.value = flatRes.data.map(c => ({
          ...c,
          indent: c.parent_collection_id ? '  └ ' : ''
        }))
      } catch (err) {
        error.value = 'Failed to load collections: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Select collection
    const selectCollection = async (collection) => {
      try {
        const response = await api.getCollection(collection.collection_id)
        selectedCollection.value = response.data
        showForm.value = false
      } catch (err) {
        error.value = 'Failed to load collection details: ' + err.message
      }
    }

    const selectCollectionById = async (id) => {
      await selectCollection({ collection_id: id })
    }

    // Available works (not in selected collection)
    const availableWorks = computed(() => {
      if (!selectedCollection.value) return works.value
      const existingIds = new Set(selectedCollection.value.works?.map(w => w.work_id) || [])
      return works.value.filter(w => !existingIds.has(w.work_id))
    })

    // Form actions
    const showCreateForm = () => {
      editingCollection.value = null
      formData.value = {
        collection_name: '',
        collection_name_tamil: '',
        collection_type: 'custom',
        description: '',
        parent_collection_id: null,
        sort_order: null
      }
      showForm.value = true
    }

    const editCollection = () => {
      editingCollection.value = selectedCollection.value
      formData.value = {
        collection_name: selectedCollection.value.collection_name,
        collection_name_tamil: selectedCollection.value.collection_name_tamil || '',
        collection_type: selectedCollection.value.collection_type,
        description: selectedCollection.value.description || '',
        parent_collection_id: selectedCollection.value.parent_collection_id,
        sort_order: selectedCollection.value.sort_order
      }
      showForm.value = true
    }

    const cancelForm = () => {
      showForm.value = false
      editingCollection.value = null
    }

    const saveCollection = async () => {
      try {
        if (editingCollection.value) {
          await api.updateCollection(editingCollection.value.collection_id, formData.value)
        } else {
          await api.createCollection(formData.value)
        }
        await loadCollections()
        showForm.value = false
        editingCollection.value = null
        if (selectedCollection.value) {
          await selectCollection(selectedCollection.value)
        }
      } catch (err) {
        error.value = 'Failed to save collection: ' + err.message
      }
    }

    // Delete collection
    const confirmDelete = () => {
      showDeleteConfirm.value = true
    }

    const deleteCollection = async () => {
      try {
        await api.deleteCollection(selectedCollection.value.collection_id)
        selectedCollection.value = null
        showDeleteConfirm.value = false
        await loadCollections()
      } catch (err) {
        error.value = 'Failed to delete collection: ' + err.message
      }
    }

    // Work management
    const addWork = async () => {
      try {
        await api.addWorkToCollection(selectedCollection.value.collection_id, addWorkData.value)
        showAddWork.value = false
        addWorkData.value = { work_id: null, position: null, is_primary: false }
        await selectCollection(selectedCollection.value)
        await loadCollections()
      } catch (err) {
        error.value = 'Failed to add work: ' + err.message
      }
    }

    const removeWork = async (workId) => {
      if (!confirm('Remove this work from the collection?')) return
      try {
        await api.removeWorkFromCollection(selectedCollection.value.collection_id, workId)
        await selectCollection(selectedCollection.value)
        await loadCollections()
      } catch (err) {
        error.value = 'Failed to remove work: ' + err.message
      }
    }

    onMounted(loadCollections)

    return {
      loading,
      error,
      collectionTree,
      flatCollections,
      selectedCollection,
      works,
      showForm,
      editingCollection,
      formData,
      showAddWork,
      addWorkData,
      showDeleteConfirm,
      availableWorks,
      selectCollection,
      selectCollectionById,
      showCreateForm,
      editCollection,
      cancelForm,
      saveCollection,
      confirmDelete,
      deleteCollection,
      addWork,
      removeWork
    }
  }
}
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.admin-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  margin-top: 20px;
}

/* Panels */
.collections-panel, .details-panel {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  min-height: 500px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.panel-header h3 {
  margin: 0;
}

/* Tree View */
.collection-tree {
  overflow-y: auto;
  max-height: calc(100vh - 250px);
}

.tree-node {
  user-select: none;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 2px;
}

.tree-item:hover {
  background: #f5f5f5;
}

.tree-item.selected {
  background: #e3f2fd;
  font-weight: 500;
}

.tree-icon {
  width: 16px;
  font-size: 10px;
  color: #666;
  margin-right: 8px;
}

.tree-name {
  flex: 1;
}

.tree-count {
  color: #888;
  font-size: 12px;
  margin-left: 8px;
}

/* Details */
.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.details-header h3 {
  margin: 0;
}

.details-actions {
  display: flex;
  gap: 8px;
}

.details-info p {
  margin: 8px 0;
}

/* Works Section */
.works-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  margin: 0;
}

.works-list {
  max-height: 300px;
  overflow-y: auto;
}

.work-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 4px;
}

.work-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.work-position {
  color: #666;
  font-size: 12px;
  min-width: 30px;
}

.primary-badge {
  background: #4caf50;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
}

.btn-remove {
  background: none;
  border: none;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  padding: 0 8px;
}

.btn-remove:hover {
  color: #d32f2f;
}

/* Form */
.collection-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}

/* Buttons */
.btn-primary {
  background: #1976d2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background: #1565c0;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #eee;
}

.btn-danger {
  background: #d32f2f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-danger:hover {
  background: #c62828;
}

.btn-small {
  padding: 4px 12px;
  font-size: 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small:hover {
  background: #eee;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
}

.warning {
  color: #f57c00;
  font-size: 14px;
}

/* Empty states */
.empty-state, .empty-works, .empty-details {
  color: #888;
  text-align: center;
  padding: 20px;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #d32f2f;
}

/* Children section */
.children-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.children-section h4 {
  margin-bottom: 12px;
}

.children-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.children-section li {
  padding: 4px 0;
}

.children-section a {
  color: #1976d2;
  text-decoration: none;
}

.children-section a:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .collections-panel {
    min-height: auto;
  }
}
</style>
