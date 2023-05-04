#ifndef DUMMY_RJSJAI_H
#define DUMMY_RJSJAI_H

#include "./real_rjsjai.h"

#ifndef __cplusplus
#error "This file is for C++ only"
#endif

#include <sstream>
#include <string>
#include <vector>
#include <cstdlib>
#include <cstring>

struct RJSJAI_ {
    std::string token;
    int status;
    std::vector<char> result;
};

extern "C" inline RJSJAI* ai_create(const char* token) {
    return new RJSJAI{token};
}

extern "C" inline int ai_send(RJSJAI* ai, int type, const char* prompt) {
    if (std::getenv("DUMMY_RJSJAI_EXPECT_ERROR")) {
        // simulate error
        ai->status = AI_ERROR_HTTP_UNKNOWN;
    } else if (type == AI_TYPE_DRAW || type == AI_TYPE_WOLFRAM ) {
        // add binary signature
        constexpr const char sig[] = "\xa1\x7e\x27\x07\x00\x0d\x0a\x67";
        ai->result.insert(ai->result.end(), sig, sig + sizeof(sig) - 1);
    }
    std::ostringstream oss;
    oss << "{\"type\":" << type << ",\"status\":" << ai->status
        << ",\"prompt\":\"" << prompt << "\"}";
    // std::quoted removed. Some student is using C++11 or lower.
    std::string body = oss.str();
    ai->result.insert(ai->result.end(), body.begin(), body.end());
    return ai->status;
}

extern "C" inline int ai_status(RJSJAI* ai) {
    return ai->status;
}

extern "C" inline int ai_result(RJSJAI* ai, char* dest) {
    if (dest) {
        std::memcpy(dest, ai->result.data(), ai->result.size());
    }
    return ai->result.size();
}

extern "C" inline void ai_free(RJSJAI* ai) {
    delete ai;
}

#endif
