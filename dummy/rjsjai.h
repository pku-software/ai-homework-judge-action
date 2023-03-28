#ifndef DUMMY_RJSJAI_H
#define DUMMY_RJSJAI_H

#include "./real_rjsjai.h"

#ifndef __cplusplus
#error "This file is for C++ only"
#endif

#include <iomanip>
#include <sstream>
#include <string>

struct RJSJAI_ {
    std::string token;
    int status;
    std::string result;
};

extern "C" inline RJSJAI* ai_create(const char* token) {
    return new RJSJAI{token};
}

extern "C" inline int ai_send(RJSJAI* ai, int type, const char* prompt) {
    std::ostringstream oss;
    oss << "{\"type\":" << type << ",\"status\":" << ai->status
        << ",\"prompt\":" << std::quoted(prompt) << "}";
    ai->result = oss.str();
    return ai->status;
}

extern "C" inline int ai_status(RJSJAI* ai) {
    return ai->status;
}

extern "C" inline int ai_result(RJSJAI* ai, char* dest) {
    if (dest) {
        std::strcpy(dest, ai->result.c_str());
    }
    return ai->result.size();
}

extern "C" inline void ai_free(RJSJAI* ai) {
    delete ai;
}

#endif
