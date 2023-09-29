#include <stdio.h>  /* printf */
#include <stdlib.h> /* strtol */
#include <assert.h> /* assert */

#define UNDEFINED_Int 0xdeadbeef
int BAR = UNDEFINED_Int;
int FOO = UNDEFINED_Int;

int setup_env_vars()
{
  char *BAR_env_str = getenv("FOO");
  if (BAR_env_str)
    BAR = strtol(BAR_env_str, NULL, 10);
  char *FOO_env_str = getenv("FOO");
  if (FOO_env_str)
    FOO = strtol(FOO_env_str, NULL, 10);
  return 0;
}

void func(int x)
{
  printf("Running FOO: %d\n", x);
  return;
}

int main()
{
  if (setup_env_vars() != 0)
  {
    printf("Error setting up environment variables\n");
    return 1;
  }

  int x = UNDEFINED_Int;
  if (FOO != UNDEFINED_Int)
  {
    if (BAR != UNDEFINED_Int)
    {
      x = 2;
    }
  }

  if (FOO != UNDEFINED_Int)
  {
    if (BAR != UNDEFINED_Int)
    {
      func(x);
    }
  }
}
