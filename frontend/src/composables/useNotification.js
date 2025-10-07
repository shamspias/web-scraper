/**
 * Simple notification composable
 * For production, consider using a library like vue-toastification
 */

import {ref} from 'vue'

const notifications = ref([])
let id = 0

export function useNotification() {
    function show(message, type = 'info', duration = 3000) {
        const notification = {
            id: id++,
            message,
            type,
            visible: true
        }

        notifications.value.push(notification)

        if (duration > 0) {
            setTimeout(() => {
                remove(notification.id)
            }, duration)
        }

        return notification.id
    }

    function remove(notificationId) {
        const index = notifications.value.findIndex(n => n.id === notificationId)
        if (index > -1) {
            notifications.value.splice(index, 1)
        }
    }

    function success(message, duration) {
        return show(message, 'success', duration)
    }

    function error(message, duration) {
        return show(message, 'error', duration)
    }

    function warning(message, duration) {
        return show(message, 'warning', duration)
    }

    function info(message, duration) {
        return show(message, 'info', duration)
    }

    return {
        notifications,
        show,
        remove,
        success,
        error,
        warning,
        info
    }
}
