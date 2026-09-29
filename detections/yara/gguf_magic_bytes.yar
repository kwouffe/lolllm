/*
  GGUF Model File Detection
  Matches the 4-byte magic number at offset 0 of GGUF-format model weight files.
  GGUF is the native format for llama.cpp-compatible inference engines including
  Ollama, LM Studio, llama.cpp, and Jan.

  Reference: https://github.com/ggerganov/ggml/blob/master/docs/gguf.md
*/

rule GGUF_ModelFile {
    meta:
        description  = "Detects GGUF format model weight files used by llama.cpp-compatible inference engines"
        author       = "lolllm-project"
        date         = "2025-01-01"
        reference    = "https://github.com/ggerganov/ggml/blob/master/docs/gguf.md"
        tlp          = "WHITE"
        tags         = "llm,gguf,inference,lolllm"

    strings:
        $magic = { 47 47 55 46 }   // ASCII: GGUF

    condition:
        $magic at 0
}

rule GGUF_ModelFile_Large {
    meta:
        description  = "Detects large GGUF model files (>500MB) — high-confidence signal for model weight storage"
        author       = "lolllm-project"
        date         = "2025-01-01"
        reference    = "https://github.com/ggerganov/ggml/blob/master/docs/gguf.md"
        tlp          = "WHITE"

    strings:
        $magic = { 47 47 55 46 }

    condition:
        $magic at 0 and filesize > 500MB
}
