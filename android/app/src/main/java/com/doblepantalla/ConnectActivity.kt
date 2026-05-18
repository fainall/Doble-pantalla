package com.doblepantalla

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import androidx.preference.PreferenceManager

class ConnectActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_connect)

        val prefs = PreferenceManager.getDefaultSharedPreferences(this)
        val input = findViewById<EditText>(R.id.serverInput)
        val button = findViewById<Button>(R.id.connectButton)

        input.setText(prefs.getString(KEY_LAST_URL, DEFAULT_URL))

        button.setOnClickListener {
            val raw = input.text.toString().trim()
            val url = normalize(raw)
            prefs.edit().putString(KEY_LAST_URL, url).apply()
            startActivity(
                Intent(this, MainActivity::class.java).putExtra(MainActivity.EXTRA_URL, url)
            )
        }
    }

    private fun normalize(raw: String): String {
        val trimmed = raw.trim().trimEnd('/')
        return when {
            trimmed.startsWith("ws://") || trimmed.startsWith("wss://") -> trimmed
            trimmed.startsWith("http://") -> "ws://" + trimmed.removePrefix("http://") + "/ws"
            trimmed.startsWith("https://") -> "wss://" + trimmed.removePrefix("https://") + "/ws"
            else -> "ws://$trimmed/ws"
        }
    }

    companion object {
        private const val KEY_LAST_URL = "last_url"
        private const val DEFAULT_URL = "192.168.1.42:8080"
    }
}
