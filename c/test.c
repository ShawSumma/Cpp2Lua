void __printn(const void *);

int main() {
    const char *x = "hello";
    while (*x) {
        __printn(*x);
        x ++;
    }
}