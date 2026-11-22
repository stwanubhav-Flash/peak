package com.itsmuzz.peakcut

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.*
import android.widget.*
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    private lateinit var web: WebView
    private val prefs by lazy { getSharedPreferences("peakcut", MODE_PRIVATE) }
    private val defaultUrl = "http://127.0.0.1:8765/app"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = android.graphics.Color.rgb(30, 22, 18)
        window.navigationBarColor = android.graphics.Color.rgb(30, 22, 18)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(android.graphics.Color.rgb(30,22,18))
        }
        val bar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(10, 8, 10, 8)
            gravity = android.view.Gravity.CENTER_VERTICAL
        }
        val settings = Button(this).apply {
            text = "Server"
            setOnClickListener { editServer() }
        }
        val reload = Button(this).apply {
            text = "Reload"
            setOnClickListener { web.reload() }
        }
        bar.addView(settings, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        bar.addView(reload)
        web = WebView(this).apply {
            this.settings.javaScriptEnabled = true
            this.settings.domStorageEnabled = true
            this.settings.allowFileAccess = true
            this.settings.mediaPlaybackRequiresUserGesture = false
            webChromeClient = WebChromeClient()
            webViewClient = object : WebViewClient() {
                override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                    if (request?.isForMainFrame == true) showOffline()
                }
            }
        }
        root.addView(bar)
        root.addView(web, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        setContentView(root)
        web.loadUrl(prefs.getString("url", defaultUrl) ?: defaultUrl)
    }

    private fun showOffline() {
        val html = """
            <html><meta name="viewport" content="width=device-width,initial-scale=1">
            <body style="font-family:sans-serif;background:#1e1612;color:#f4eeea;padding:28px">
            <h2>PeakCut server not reachable</h2>
            <p>This Android app opens your original PeakCut dashboard. The PeakCut Python backend must be running at the configured server address.</p>
            <p>Tap <b>Server</b> above to change the address, then tap Reload.</p>
            </body></html>
        """.trimIndent()
        runOnUiThread { web.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null) }
    }

    private fun editServer() {
        val input = EditText(this).apply {
            setSingleLine(true)
            setText(prefs.getString("url", defaultUrl))
            hint = "http://192.168.1.10:8765/app"
        }
        AlertDialog.Builder(this)
            .setTitle("PeakCut server address")
            .setMessage("Enter the address where your PeakCut backend is running.")
            .setView(input)
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Save") { _, _ ->
                val value = input.text.toString().trim()
                if (value.startsWith("http://") || value.startsWith("https://")) {
                    prefs.edit().putString("url", value).apply()
                    web.loadUrl(value)
                } else Toast.makeText(this, "Enter a valid http:// or https:// address", Toast.LENGTH_LONG).show()
            }.show()
    }

    override fun onBackPressed() {
        if (::web.isInitialized && web.canGoBack()) web.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        if (::web.isInitialized) web.destroy()
        super.onDestroy()
    }
}
