--- ../../yajsw-12.16_unmodified/src/groovy-patch/src/main/java/org/codehaus/groovy/runtime/DefaultGroovyMethods.java	2021-04-19 16:10:42.000000000 -0400
+++ ../src/groovy-patch/src/main/java/org/codehaus/groovy/runtime/DefaultGroovyMethods.java	2021-08-12 13:10:07.199402745 -0400
@@ -11933,6 +11933,12 @@
 
     /**
      * Create an array as a union of two arrays.
+     *
+     * bkowal: This method has been updated so that non-compiling code would not
+     * be committed to the baseline. There was probably no issues with the older
+     * versions of Java that YAJSW still supports. Without this change, there
+     * were ambiguous method errors.
+     *
      * <pre class="groovyTestCase">
      * Integer[] a = [1, 2, 3]
      * Integer[] b = [4, 5, 6]
@@ -11946,7 +11952,12 @@
      */
     @SuppressWarnings("unchecked")
     public static <T> T[] plus(T[] left, T[] right) {
-        return (T[]) plus(toList(left), toList(right)).toArray();
+        List<T> leftList = toList(left);
+        List<T> rightList = toList(right);
+        final Collection<T> answer = cloneSimilarCollection(leftList,
+                 leftList.size() + rightList.size());
+        answer.addAll(rightList);
+        return (T[]) answer.toArray();
     }
 
     /**
@@ -11969,6 +11980,12 @@
 
     /**
      * Create an array containing elements from an original array plus those from a Collection.
+     *
+     * bkowal: This method has been updated so that non-compiling code would not
+     * be committed to the baseline. There was probably no issues with the older
+     * versions of Java that YAJSW still supports. Without this change, there
+     * were ambiguous method errors.
+     *
      * <pre class="groovyTestCase">
      * Integer[] a = [1, 2, 3]
      * def additions = [7, 8]
@@ -11982,11 +11999,22 @@
      */
     @SuppressWarnings("unchecked")
     public static <T> T[] plus(T[] left, Collection<T> right) {
-        return (T[]) plus(toList(left), right).toArray();
+        List<T> leftList = toList(left);
+        List<T> rightList = toList(right);
+        final Collection<T> answer = cloneSimilarCollection(leftList,
+                leftList.size() + rightList.size());
+        answer.addAll(rightList);
+        return (T[]) answer.toArray();
     }
 
     /**
      * Create an array containing elements from an original array plus those from an Iterable.
+     *
+     * bkowal: This method has been updated so that non-compiling code would not
+     * be committed to the baseline. There was probably no issues with the older
+     * versions of Java that YAJSW still supports. Without this change, there
+     * were ambiguous method errors.
+     *
      * <pre class="groovyTestCase">
      * class AbcIterable implements Iterable<String> {
      *     Iterator<String> iterator() { "abc".iterator() }
@@ -12004,7 +12032,12 @@
      */
     @SuppressWarnings("unchecked")
     public static <T> T[] plus(T[] left, Iterable<T> right) {
-        return (T[]) plus(toList(left), toList(right)).toArray();
+        List<T> leftList = toList(left);
+        List<T> rightList = toList(right);
+        final Collection<T> answer = cloneSimilarCollection(leftList,
+                leftList.size() + rightList.size());
+        answer.addAll(rightList);
+        return (T[]) answer.toArray();
     }
 
     /**
