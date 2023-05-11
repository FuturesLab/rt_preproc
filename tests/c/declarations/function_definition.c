#include <stdio.h>

#ifdef FOO
  void foo(){
    printf("foo");
  }
#endif 
 
int main(){
  #ifdef FOO
    foo();
  #endif
}
