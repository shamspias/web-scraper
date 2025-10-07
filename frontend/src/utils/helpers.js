/**
 * Utility helper functions
 */

/**
 * Format date to readable string
 */
export function formatDate(date, includeTime = true) {
    if (!date) return 'N/A'

    const d = new Date(date)

    if (isNaN(d.getTime())) return 'Invalid Date'

    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...(includeTime && {
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return d.toLocaleString('en-US', options)
}

/**
 * Format bytes to human readable
 */
export function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Get domain from URL
 */
export function getDomainFromUrl(url) {
    try {
        const urlObj = new URL(url)
        return urlObj.hostname.replace('www.', '')
    } catch {
        return url
    }
}

/**
 * Truncate text
 */
export function truncate(text, length = 100) {
    if (!text) return ''
    if (text.length <= length) return text
    return text.substring(0, length) + '...'
}

/**
 * Calculate reading time
 */
export function calculateReadingTime(text) {
    if (!text) return 0
    const wordsPerMinute = 200
    const words = text.split(/\s+/).length
    return Math.ceil(words / wordsPerMinute)
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout)
            func(...args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

/**
 * Copy to clipboard
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text)
        return true
    } catch (err) {
        console.error('Failed to copy:', err)
        return false
    }
}

/**
 * Download as JSON
 */
export function downloadJSON(data, filename = 'data.json') {
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], {type: 'application/json'})
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
}

/**
 * Download as CSV
 */
export function downloadCSV(data, filename = 'data.csv') {
    const csv = convertToCSV(data)
    const blob = new Blob([csv], {type: 'text/csv'})
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
}

function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) return ''

    const headers = Object.keys(data[0])
    const rows = data.map(row =>
        headers.map(header => {
            const value = row[header]
            return typeof value === 'string' && value.includes(',')
                ? `"${value}"`
                : value
        }).join(',')
    )

    return [headers.join(','), ...rows].join('\n')
}
