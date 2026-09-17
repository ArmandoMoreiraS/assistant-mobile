package com.aicompanion.ai_companion_app

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class ScreenContextService : AccessibilityService() {

    companion object {
        var currentScreenText: String = ""
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val rootNode = rootInActiveWindow
        if (rootNode != null) {
            val sb = StringBuilder()
            extractText(rootNode, sb)
            currentScreenText = sb.toString().trim()
        }
    }

    private fun extractText(node: AccessibilityNodeInfo, sb: StringBuilder) {
        if (node.text != null && node.text.isNotEmpty()) {
            sb.append(node.text).append("\n")
        } else if (node.contentDescription != null && node.contentDescription.isNotEmpty()) {
            sb.append(node.contentDescription).append("\n")
        }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                extractText(child, sb)
            }
        }
    }

    override fun onInterrupt() {
        // Nada que hacer aquí
    }
}
